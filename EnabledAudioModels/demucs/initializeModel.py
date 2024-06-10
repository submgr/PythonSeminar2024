import os
import subprocess

subprocess.check_call(["pip", "install", "-r", os.path.dirname(os.path.realpath(__file__)) + "/requirements.txt"])

import zipfile
import sys

# Unzip the archive
with zipfile.ZipFile(os.path.dirname(os.path.realpath(__file__)) + '/demucs_pymodel.zip', 'r') as zip_ref:
    zip_ref.extractall('temp')

# Install PyTorch and torchaudio
# Replace the following command with the one you get from the PyTorch official website
subprocess.check_call(['pip', 'install', 'torch==2.2.0'])
subprocess.check_call(['pip', 'install', 'torchaudio==2.2.0'])


import imageio_ffmpeg as ffmpeg
import shutil

# Install the package from the local archive
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-U', os.path.dirname(os.path.realpath(__file__)) + '/temp'])

# Check if conda is installed
if os.system('conda --version') == 0:
    # Update conda environment
    os.system('conda env update -f ./temp/environment-cpu.yml')  # if you don't have GPUs
    os.system('conda env update -f ./temp/environment-cuda.yml')  # if you have GPUs

    # Activate conda environment
    os.system('conda activate demucs')