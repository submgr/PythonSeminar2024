import os
import sys
import subprocess
import argparse
import shutil
import hashlib
from pathlib import Path

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--savepath', required=True, help='Output path (folder)')
parser.add_argument('--sourcepath', required=True, help='Output path (folder)')
args = parser.parse_args()

def get_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()



# Check if the demucs module and example_noisy.mp3 file exist
if not os.path.isfile(sys.executable):
    print("demucs module or example_noisy.mp3 file doesn't exist")
    sys.exit(1)

# Run the demucs module with the updated environment variables
subprocess.run([sys.executable, '-m', 'demucs', '--mp3', '--two-stems=vocals', args.sourcepath, '-o', os.path.dirname(os.path.realpath(__file__)) + '/tempData/'], env=os.environ)

filename = Path(args.sourcepath).stem

# Check if the source file exists before trying to move it
source_file = os.path.dirname(os.path.realpath(__file__)) + '/tempData/htdemucs/' + filename + '/vocals.mp3'
if not os.path.isfile(source_file):
    print("Source file doesn't exist: " + source_file)
    sys.exit(1)

# Move the vocals.mp3 file from tempData to the folder specified by --filename
# Check if the file already exists at the destination
if os.path.exists(args.savepath):
    print("File already exists at the destination.")
else:
    shutil.move(source_file, args.savepath)