"""
WSGI wrapper for Gunicorn to serve the Flask app.
"""
import sys
from pathlib import Path

file = Path(__file__)
parent = file.parent
ROOT = None
for parent in file.parents:
    if parent.name == "ChunkChariot":
        ROOT = parent
sys.path.append(str(ROOT))

from uploader.app import create_app
from uploader.helpers import utils

# Get the configuration file path
config_file = utils.get_config_file_path()

# Create the Flask app instance
app = create_app(config_file=config_file)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
