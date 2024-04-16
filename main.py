from flask import Flask, send_from_directory, request
from pathlib import Path
from werkzeug.utils import secure_filename

import os

import uuid

UPLOAD_DIR: Path = Path(__file__).parent / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, static_folder='static/ionicwebwrapper/NoiseReducer/dist/')

def is_valid_upload(upload) -> bool:
    # some validation logic
    return Path(upload.filename).suffix.lower() in ['.mp3', '.jpeg', ".png"]

@app.route('/')
def serve_index():
    return send_from_directory('static/', 'weblayer.html')

@app.route('/static/')
def serve_staticindex():
    return send_from_directory('static/ionicwebwrapper/NoiseReducer/dist/', 'index.html')

@app.route('/static/assets/<path:path>')
def serve_files(path):
    return send_from_directory('static/ionicwebwrapper/NoiseReducer/dist/assets/', path)

@app.route('/fileUploadTemporary', methods=['POST'])
def upload():

    uploaded_files = request.files.getlist('assets')
    if not uploaded_files or not uploaded_files[0].filename:
        return 'invalid asset(s), error code: 0001', 400

    valid_uploads = list(filter(is_valid_upload, uploaded_files))
    if not valid_uploads:
        return 'invalid asset(s), error code: 0002', 400

    for upload in valid_uploads:
        filename = secure_filename(upload.filename)
        private_fileuuid = str(uuid.uuid4());
        filename = private_fileuuid + filename
        save_path = str(UPLOAD_DIR / filename)

        upload.save(save_path)

        return filename

@app.route('/fileCheckOutput/<path:filename>', methods=['GET'])
def check(filename):
    filename = str(UPLOAD_DIR / filename)
    if os.path.isfile(filename):
        return 'the requested file is ready to be downloaded as soon as possible (remark: files are getting deleted from the system after short period of time)', 200
    else:
        return 'unable to find the requested output file at this moment', 202
    
@app.route('/fileGetOutput/<path:filename>', methods=['GET'])
def download(filename):
    filename = str(UPLOAD_DIR / filename)
    if os.path.isfile(filename):
        directory, filename = os.path.split(filename)
        return send_from_directory(directory, filename, as_attachment=True)
    else:
        return 'this doesnt exist, maybe it was deleted nor never existed at all', 404
    

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(port=5000)