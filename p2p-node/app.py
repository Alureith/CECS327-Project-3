# Import necessary modules from Flask
from flask import Flask, request, jsonify, send_file, send_from_directory
import os
import hashlib
import socket
import requests
import time
import threading
import json

# Create the Flask app instance
app = Flask(__name__)

# Flask key-value pairs
key_storage = {}

# Make sure the storage folder exists to save uploaded files
os.makedirs('./storage', exist_ok=True)

# Track peers and own identity
peers = set()

own_ip = socket.gethostbyname(socket.gethostname())
own_url = f"http://{own_ip}:5000"

# Bootstrap registration (optional role check)
bootstrap_url = os.getenv("BOOTSTRAP", "http://bootstrap:5000")

metrics = {
    "ping_count": 0,
    "kv_get": 0,
    "kv_post": 0,
    "gossip_sent": 0,
    "gossip_received": 0
}


def register_with_bootstrap():
    try:
        res = requests.post(f"{bootstrap_url}/peers", json={"peers": [own_url]})
        response_data = res.json()
        added = 0
        for peer in response_data.get("current_peers", []):
            if peer != own_url and peer not in peers:
                peers.add(peer)
                added += 1
        print(f"Registered with bootstrap, {added} peers added: {peers}")
    except Exception as e:
        print(f"Bootstrap registration failed: {e}")

# Helper function to find responsible node
def hash_key_to_node(key):
    if not peers:
        return own_url  # Fallback for single node

    hash_val = hashlib.sha1(key.encode()).hexdigest()
    sorted_peers = sorted(peers | {own_url}, key=lambda p: hashlib.sha1(p.encode()).hexdigest())
    for peer in sorted_peers:
        if hashlib.sha1(key.encode()).hexdigest() <= hashlib.sha1(peer.encode()).hexdigest():
            return peer
    return sorted_peers[0]

# Route to handle file uploads
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save(f"./storage/{file.filename}")
    return jsonify({"status": "uploaded", "filename": file.filename})

# Route to handle file downloads
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory('./storage', filename)

@app.route('/kv', methods=['POST'])
def store_key_value():
    metrics["kv_post"] += 1
    data = request.get_json()
    key = data.get('key')
    value = data.get('value')

    if not key or not value:
        return jsonify({"error": "Missing key or value"}), 400

    responsible_node = hash_key_to_node(key)

    if responsible_node != own_url:
        try:
            res = requests.post(f"{responsible_node}/kv", json=data)
            return res.json(), res.status_code
        except Exception as e:
            return jsonify({"error": f"Forwarding failed: {str(e)}"}), 500

    key_storage[key] = value
    return jsonify({"status": "stored locally", "key": key, "value": value})

@app.route('/kv/<key>', methods=['GET'])
def get_value(key):
    metrics["kv_get"] += 1
    responsible_node = hash_key_to_node(key)

    if responsible_node != own_url:
        try:
            res = requests.get(f"{responsible_node}/kv/{key}")
            return res.json(), res.status_code
        except Exception as e:
            return jsonify({"error": f"Forwarding failed: {str(e)}"}), 500

    value = key_storage.get(key)
    if value:
        return jsonify({"key": key, "value": value})
    else:
        return jsonify({"error": "Key not found"}), 404

@app.route('/peers', methods=['POST'])
def update_peers():
    data = request.get_json()
    if not data or "peers" not in data or not isinstance(data["peers"], list):
        return jsonify({"error": "Invalid input, expected a JSON object with a 'peers' list"}), 400

    added = []
    for p in data["peers"]:
        if p != own_url and p not in peers:
            peers.add(p)
            added.append(p)

    return jsonify({
        "status": "peers updated",
        "added": added,
        "current_peers": list(peers)
    })

# Health check endpoint
@app.route('/ping', methods=['GET'])
def ping():
    metrics["ping_count"] += 1
    sender = request.args.get("sender")
    if sender and sender != own_url and sender not in peers:
        peers.add(sender)
        print(f"Added peer from ping: {sender}")
        # Notify sender back
        try:
            requests.post(f"{sender}/peers", json={"peers": [own_url]})
        except Exception as e:
            print(f"Failed to notify sender {sender}: {e}")

    return jsonify({"status": "alive", "node": own_url})

# Notify other peers of this node's existence
def notify_peers():
    for peer in list(peers):
        if peer == own_url:
            continue
        for attempt in range(5):
            try:
                res = requests.post(f"{peer}/peers", json={"peers": [own_url]})
                print(f"Notified {peer}: {res.text}")
                break
            except Exception as e:
                print(f"Failed to notify {peer} (attempt {attempt + 1}/5): {e}")
                time.sleep(3)

def monitor_peers():
    while True:
        time.sleep(10)
        dead_peers = []
        for peer in list(peers):
            if peer == own_url:
                continue
            try:
                res = requests.get(f"{peer}/ping", params={"sender": own_url}, timeout=3)
                if res.status_code != 200:
                    raise Exception(f"Non-200 status: {res.status_code}")
                try:
                    data = res.json()
                except ValueError:
                    raise Exception("Invalid JSON in ping response")

                if data.get("status") != "alive":
                    raise Exception("Ping status not alive")
            except Exception as e:
                print(f"[{own_url}] Removing unresponsive peer: {peer} ({e})")
                dead_peers.append(peer)
        for dead in dead_peers:
            peers.discard(dead)
            for peer in list(peers):
                try:
                    requests.post(f"{peer}/peers", json={"remove": [dead]})
                except Exception as e:
                    print(f"[{own_url}] Failed to notify {peer} about dead peer {dead}: {e}")

@app.route('/gossip', methods=['POST'])
def receive_gossip():
    data = request.get_json()
    received_peers = data.get("peers", [])
    ttl = data.get("ttl", 0)

    added = []
    for p in received_peers:
        if p != own_url and p not in peers:
            peers.add(p)
            added.append(p)

    print(f"Received gossip. Peers added: {added}")
    metrics["gossip_received"] += 1
    if ttl > 0:
        import random
        others = list(peers - {own_url})
        if others:
            forward_to = random.choice(others)
            try:
                requests.post(f"{forward_to}/gossip", json={"peers": list(peers), "ttl": ttl - 1})
                print(f"Forwarded gossip to {forward_to}")
            except Exception as e:
                print(f"Gossip forward to {forward_to} failed: {e}")

    return jsonify({"status": "gossip received", "added": added, "ttl": ttl})

def gossip_peers():
    while True:
        time.sleep(15)
        metrics["gossip_sent"] += 1
        if not peers:
            continue
        import random
        target = random.choice(list(peers))
        try:
            requests.post(f"{target}/gossip", json={"peers": list(peers), "ttl": 2})
            print(f"Gossiped peer list to {target}")
        except Exception as e:
            print(f"Gossip to {target} failed: {e}")
from datetime import datetime

metrics_data = {
    "gossip_sent": [],
    "ping_counts": [],
    "timestamps": []
}

def log_metric(key):
    now = datetime.now().strftime("%H:%M")
    if len(metrics_data[key]) >= 10:
        metrics_data[key].pop(0)
        metrics_data["timestamps"].pop(0)
    metrics_data[key].append(metrics_data[key][-1] + 1 if metrics_data[key] else 1)
    if key == "ping_counts" or key == "gossip_sent":
        metrics_data["timestamps"].append(now)

@app.route("/metrics")
def get_metrics():
    return jsonify({
        "active_peers": len(peers),
        "gossip_sent": metrics_data["gossip_sent"],
        "ping_counts": metrics_data["ping_counts"],
        "timestamps": metrics_data["timestamps"]
    })

@app.route('/dashboard')
def dashboard():
    return send_file('dashboard.html')


# Run the app
if __name__ == '__main__':
    time.sleep(1)
    register_with_bootstrap()
    notify_peers()
    threading.Thread(target=monitor_peers, daemon=True).start()
    threading.Thread(target=gossip_peers, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
