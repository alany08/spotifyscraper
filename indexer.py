#index all files in the directory
import os
from metadata import get_metadata, get_bitrate
import shutil
from config import config
import re

def get_all_files(directory):
	files = set()
	for (dirpath, dirnames, filenames) in os.walk(directory):
		for filename in filenames:
			files.add(dirpath + "/" + filename)
	return list(files)

def sanitize_filename(filename):
    invalid_chars = r'[<>:"/\\|?*\x00-\x1F]'
    
    sanitized = re.sub(invalid_chars, '_', filename)
    
    name, ext = os.path.splitext(sanitized)
    sanitized = f"{name}{ext}"
    
    return sanitized

def rename_files_by_metadata(files):
	for f in files:
		ext = f.split(".")[-1]
		dirname = os.path.split(f)[0]
		metadata = get_metadata(f)
		if f != dirname + "/" + sanitize_filename(f"{metadata.name} - {", ".join(metadata.artists)}.{metadata.isrc}.{ext}"):
			print("Moving", f, "to", dirname + "/" + sanitize_filename(f"{metadata.name} - {", ".join(metadata.artists)}.{metadata.isrc}.{ext}"))
			shutil.copy2(f, dirname + "/" + sanitize_filename(f"{metadata.name} - {", ".join(metadata.artists)}.{metadata.isrc}.{ext}"))
			os.remove(f)
		else:
			print("No need to move", f)

def flatten_to(sourcedir, destinationdir):
	files = get_all_files(sourcedir)
	for f in files:
		if f.split(".")[-1] in config["accepted_file_extensions"]:
			print("Copying", f)
			shutil.copy2(f, destinationdir + "/" + os.path.split(f)[1])