import metadata
import indexer
import spotify
from track import Track
from config import config
from manual_isrc import defined_songs
import json
import os
import sys

indexer.flatten_to(config["music_root_directory"], config["target_music_directory"] + "/songs")

all_files = indexer.get_all_files(config["target_music_directory"] + "/songs")

_SONGS_ = {
	# ISRC: class Track
}
"""
_SONGS_ = {
	"isrc": {
		"highest_bitrate_path": "...",
		"highest_bitrate": 160000,
		"paths": [
			"all paths other than highest bitrate path"
		],
		"track": Track()
	}
}
"""
for file in all_files:

	data = metadata.get_metadata(file)
	if not data.isrc:
		print("ISRC not found for", file)
		success = False
		try:
			if(defined_songs[data.name]):
				print("Found a predefined ISRC!")
				data.isrc = defined_songs[data.name]
				success = True
		except:
			pass
		if not success:
			print("Searching spotify for ISRC of", data.name, "by", data.artists)
			try:
				data = spotify.search_for_track(name = data.name, artist = ("" if len(data.artists) == 0 else data.artists[0]))
				metadata.write_metadata(file, data)
			except Exception:
				print("Maybe the artist didn't work, trying again with only name")
				data = spotify.search_for_track(name = data.name)

	already_exists = False
	try:
		if _SONGS_[data.isrc]:
			print("Already encountered", data.isrc)
			already_exists = True
	except Exception:
		pass

	if already_exists:
		if _SONGS_[data.isrc]["highest_bitrate"] < metadata.get_bitrate(file):
			print(file, "has a superior bitrate, modifying!")
			_SONGS_[data.isrc]["highest_bitrate"] = metadata.get_bitrate(file)
			_SONGS_[data.isrc]["paths"].append(_SONGS_[data.isrc]["highest_bitrate_path"])
			_SONGS_[data.isrc]["highest_bitrate_path"] = file
			_SONGS_[data.isrc]["track"] = data
		else:
			_SONGS_[data.isrc]["paths"].append(file)
	else:
		print("Creating new entry for", data.isrc)
		_SONGS_[data.isrc] = {
			"highest_bitrate_path": file,
			"highest_bitrate": metadata.get_bitrate(file),
			"paths": [],
			"track": data
		}

#dump the result
new_songs = {}
for isrc in _SONGS_.keys():
	new_songs[isrc] = _SONGS_[isrc]
	new_songs[isrc]["track"] = json.loads(str(new_songs[isrc]["track"]))

with open("index.json", "w") as f:
	json.dump(new_songs, f, indent = 4)

to_remove = []
for isrc in _SONGS_.keys():
	for path in _SONGS_[isrc]["paths"]:
		to_remove.append(path)

print(f"Found {len(to_remove)} duplicates, they will be removed!")
input("Finished indexing all songs, press enter to continue")

for f in to_remove:
	print("Removing lower bitrate duplicate:", f)
	os.remove(f)

input("Finished cleaning up duplicate songs, press enter to continue")

all_files = indexer.get_all_files(config["target_music_directory"] + "/songs")

for file in all_files:
	data = metadata.get_metadata(file)
	if not data.spotify_id:
		print("Did not request metadata from spotify yet for", data.isrc, data.name)
		try:
			data = spotify.search_for_track(isrc = data.isrc)
		except Exception:
			print("Looks like ISRC failed, looking up via name and artist")
			try:
				data = spotify.search_for_track(name = data.name, artist = data.artists[0])
			except Exception:
				print("Looks like looking up with the artist and name didn't work either, trying only name")
				try:
					data = spotify.search_for_track(name = data.name)
				except Exception as e:
					print("Unable to lookup metadata for", data.isrc, data.name, "due to reason", e)
					print("Skipping...")
		metadata.write_metadata(file, data)
	else:
		print("Already have spotify's metadata for", data.isrc, data.name, "skipping it!")