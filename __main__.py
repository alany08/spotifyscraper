import metadata
import indexer
import spotify
from track import Track
from config import config
from manual_isrc import defined_songs
import json
import os
import sys
import shutil
import convert
import threading
import time

def nothing(a):
	return "y"

input = nothing
#temporary noconfirm

if not os.path.exists(config["target_music_directory"] + "/songs"):
	os.mkdir(config["target_music_directory"] + "/songs")

if len(os.listdir(config["target_music_directory"] + "/songs")) != 0:
	yn = input("Directory already contains songs, would you like to remove all of them? [y/N]: ")
	if not yn or yn.lower() == "n":
		print("Cannot continue, user aborted request to remove all existing songs")
		sys.exit()
	else:
		shutil.rmtree(config["target_music_directory"] + "/songs")
		os.mkdir(config["target_music_directory"] + "/songs")

if not os.path.exists("tmp"):
	os.mkdir("tmp")

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
			if defined_songs[data.name]:
				print("Found a predefined ISRC!")
				data.isrc = defined_songs[data.name]
				metadata.write_metadata(file, data)
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

with open("tmp/index.json", "w") as f:
	json.dump(new_songs, f, indent = 4)

to_remove = []
for isrc in _SONGS_.keys():
	for path in _SONGS_[isrc]["paths"]:
		to_remove.append(path)

print("An index of all your files (PRIOR TO CLEANING) can be found in tmp/index.json")
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
			if data.isrc:
				data = spotify.search_for_track(isrc = data.isrc)
			else:
				print("No ISRC found in file, let's continue to using the name")
				raise Exception()
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

input("Finished processing metadata for " + str(len(all_files)) + " files. Press enter to continue")

indexer.rename_files_by_metadata(all_files)

input("Finished renaming " + str(len(all_files)) + " files. Press enter to continue")

music_files = {
	"isrc": "filepath"
}

all_files = indexer.get_all_files(config["target_music_directory"] + "/songs")

for file in all_files:
	if not file.endswith("mp3"):
		print("Queuing convert:", file)
		convert.convert(i=file, o=os.path.splitext(file)[0] + '.mp3', bitrate=config["output_bitrate"], total=len(all_files))

while threading.active_count() != 1:
	print(f"Active threads: {threading.active_count() - 1} Processed: {convert._processed_count}/{len(all_files)}", end=f"{' '*50}\r", flush=True)
	time.sleep(0.01)

sys.stdout.flush()
os.system("reset")

input("\n\rFinished converting all files to mp3, press enter to continue")

all_files = indexer.get_all_files(config["target_music_directory"] + "/songs")

for file in all_files:
	print("Reindexing", file)
	data = metadata.get_metadata(file)
	music_files[data.isrc] = file

input("Finished reindexing " + str(len(all_files)) + " files. Press enter to continue")

notfoundstr = ""

for playlist in config["playlist_ids"]:
	playlist_name = spotify.get_playlist_name(playlist)
	print("Creating m3u playlist for playlist", playlist, playlist_name)
	playlist_items = spotify.get_playlist_tracks(playlist)
	print("Found", len(playlist_items), "items in playlist")
	playlist_text = "#EXTM3U"
	for item in playlist_items:
		try:
			#Ignore runtime, lol
			playlist_text = playlist_text + f"\n\n#EXTINF:1,{item.name}\n./songs/{os.path.split(music_files[item.isrc])[1]}"
		except KeyError:
			print("This song from", playlist_name, "was not found in your library:\n" + str(item))
			notfoundstr = notfoundstr + f"PLAYLIST: {playlist_name}\n{str(item)}\n"
	with open(config["target_music_directory"] + "/" + indexer.sanitize_filename(playlist_name + ".m3u8"), "w") as playlist_file:
		playlist_file.write(playlist_text)

with open("tmp/notfound.txt", "w") as notfound:
	notfound.write(notfoundstr)

print("A list of all the songs from playlists that were not found can be found in tmp/notfound.txt")
print("All done! Playlists are in the root directory, songs are in songs/")