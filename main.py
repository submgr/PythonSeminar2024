from flask import Flask, send_from_directory, request
from flask_cors import CORS
from pathlib import Path
from werkzeug.utils import secure_filename

import subprocess

import os
import sys

import uuid

STATIC_DISTRESOURCE_DIR = 'static/ionicwebwrapper/NoiseReducer/dist/'

# Define the paths
models_dir = Path(__file__).parent / 'EnabledAudioModels'
known_models_file = Path(__file__).parent / '.knownmodels'

# Ensure .knownmodels file exists
known_models_file.touch(exist_ok=True)

# Read the known models
with open(known_models_file, 'r') as f:
    known_models = f.read().split(',')
    
# Iterate over the folders in the models directory
for folder in [f for f in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, f))]:
    if folder not in known_models:
        # Execute init.py in the new model's folder
        init_file = os.path.join(models_dir, folder, 'initializeModel.py')

        subprocess.run([sys.executable, init_file])

        # Add the new model to the list
        known_models.append(folder)
        

# Write the updated list back to the .knownmodels file
with open(known_models_file, 'w') as f:
    f.write(','.join(known_models))

if not os.path.isdir(STATIC_DISTRESOURCE_DIR):
    print("\033[91mError: Directory {} does not exist.\nPlease, make sure to bundle this instance with the copy of Vue Frontend's Dist Resources in the stated path before.\033[0m".format(STATIC_DISTRESOURCE_DIR))
    sys.exit(1)

UPLOAD_DIR: Path = Path(__file__).parent / 'uploads'
OUTPUT_DIR: Path = Path(__file__).parent / 'output'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, static_folder=STATIC_DISTRESOURCE_DIR)
CORS(app)

def is_valid_upload(upload) -> bool:
    # some validation logic
    return Path(upload.filename).suffix.lower() in ['.mp3', '.jpeg', ".png"]

@app.route('/')
def serve_index():
    return send_from_directory('static/', 'weblayer.html')

@app.route('/static/')
def serve_staticindex():
    return send_from_directory(STATIC_DISTRESOURCE_DIR, 'index.html')

@app.route('/static/assets/<path:path>')
def serve_files(path):
    return send_from_directory(STATIC_DISTRESOURCE_DIR + 'assets/', path)

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

        command = [sys.executable, "EnabledAudioModels/demucs/executeModel.py", "--sourcepath", save_path, "--savepath", os.path.abspath("output/" + filename)]
        subprocess.Popen(command)

        return filename

@app.route('/fileCheckOutput/<path:filename>', methods=['GET'])
def check(filename):
    filename = str(OUTPUT_DIR / filename)
    if os.path.isfile(filename):
        return 'the requested file is ready to be downloaded as soon as possible (remark: files are getting deleted from the system after short period of time)', 200
    else:
        return 'unable to find the requested output file at this moment', 202
    
@app.route('/fileGetOutput/<path:filename>', methods=['GET'])
def download(filename):
    filename = str(OUTPUT_DIR / filename)
    if os.path.isfile(filename):
        directory, filename = os.path.split(filename)
        return send_from_directory(directory, filename, as_attachment=True)
    else:
        return 'this doesnt exist, maybe it was deleted nor never existed at all', 404
    

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8085))
    from waitress import serve
    print(f"\033[92mServer is running right now. \n\nDeveloped by Aram Virabyan\naevirabian@edu.hse.ru\nhttps://t.me/virabyanaram\n\033[0m")
    if 'PORT' in os.environ:
        print(f"\033[92mRunning on custom port: {port}\033[0m")
    else:
        print(f"\033[92mRunning on default port: {port}\033[0m")
    serve(app, host="0.0.0.0", port=port)