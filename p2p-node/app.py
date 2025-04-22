# Import necessary modules from Flask
from flask import Flask, request, jsonify, send_from_directory
import os

# Create the Flask app instance
app = Flask(__name__)

# Flask key-value pairs
key_storage = {}

# Make sure the storage folder exists to save uploaded files
os.makedirs('./storage', exist_ok=True)


# Route to handle file uploads
@app.route('/upload', methods=['POST'])
def upload_file():
    # Get the uploaded file from the request
    file = request.files['file']

    # Save the file to the local storage folder
    file.save(f"./storage/{file.filename}")

    # Return a JSON response confirming the upload
    return jsonify({
        "status": "uploaded",
        "filename": file.filename
    })


# Route to handle file downloads
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # Send the requested file from the storage folder
    return send_from_directory('./storage', filename)

# Set up flask endpoint to read values
@app.route('/kv', methods=['POST'])
def store_key_value():
    data = request.get_json()
    key = data.get('key')
    value = data.get('value')

    if key and value:
        key_storage[key] = value
        return jsonify({"status": "success", "key": key, "value": value})
    else:
        return jsonify({"status": "error", "message": "Invalid input"}), 400

# Recieve key value being stored 
@app.route('/kv/<key>', methods=['GET'])
def get_value(key):
    value = key_storage.get(key)
    if value:
        return jsonify({"key": key, "value": value})
    else:
        return jsonify({"error": "Key not found"}), 404

# Run the app on all network interfaces, port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
