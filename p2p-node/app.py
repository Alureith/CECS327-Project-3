# Import necessary modules from Flask
from flask import Flask, request, jsonify, send_from_directory
import os

# Create the Flask app instance
app = Flask(__name__)

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


# Run the app on all network interfaces, port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
