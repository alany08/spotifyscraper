#index all files in the directory
import os
from metadata import get_metadata, get_bitrate
import shutil
from config import config

def get_all_files(directory):
	files = set()
	for (dirpath, dirnames, filenames) in os.walk(directory):
		for filename in filenames:
			files.add(dirpath + "/" + filename)
	return list(files)

def rename_files_by_metadata(files):
	for f in files:
		ext = f.split(".")[-1]
		dirname = os.path.split(f)[0]
		metadata = get_metadata(f)
		os.rename(f, dirname + f"/{metadata.name} - {", ".join(metadata.artists)}.{ext}")

def flatten_to(sourcedir, destinationdir):
	files = get_all_files(sourcedir)
	for f in files:
		if f.split(".")[-1] in config["accepted_file_extensions"]:
			print("Copying", f)
			shutil.copy2(f, destinationdir + "/" + os.path.split(f)[1])

def dedupe_by_isrc(flattened_dir):
	files = get_all_files(flattened_dir)
	songs = {
		"isrc": {
			"highest_bitrate_path": "...",
			"highest_bitrate": 160000,
			"paths": [
				"all paths other than highest bitrate path"
			]
		}
	}