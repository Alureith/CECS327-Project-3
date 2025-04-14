from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)
os.makedirs('./storage', exist_ok=True)  # create storage dir if not exists

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save(f"./storage/{file.filename}")
    return jsonify({"status": "uploaded", "filename": file.filename})

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory('./storage', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
