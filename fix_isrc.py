import metadata
import indexer
from config import config
import spotify
import os

input("This script WILL modify files from the source directory, press enter to confirm and continue.")

all_files = indexer.get_all_files(config["music_root_directory"])

for file in all_files:
	if not file.split(".")[-1] in config["accepted_file_extensions"]:
		continue
	data = metadata.get_metadata(file)
	good = False
	if data.isrc:
		try:
			spotify.search_for_track(isrc = data.isrc)
			print("OK:", file)
			good = True
		except Exception as e:
			pass
	if not good:
		print("File:", file)
		found_songs = spotify.search_for_track(name = data.name, artist = data.artists[0], all_results = True)
		found_songs = found_songs[:5]
		for i in range(len(found_songs)):
			song = found_songs[i]
			print(f"{str(i)}:\n\tNAME: {song.name}\n\tISRC: {song.isrc}\n\tARTISTS: {str(song.artists)}\n\tALBUM: {song.album}\n\tRELEASE DATE: {song.release_date}\n\tSPOTIFY LINK: https://open.spotify.com/track/{song.spotify_id}")
		print("x: skip this song")
		print("e: enter custom ISRC")
		print("p: play the local file using MPV")
		actionable_input = ""
		while not actionable_input:
			res = input("Make your selection: ")
			if not res in ["0", "1", "2", "3", "4", "x", "e", "p"]:
				continue
			if not res == "p":
				actionable_input = res
			else:
				os.system(f"mpv --really-quiet \"{file}\"")
		if actionable_input.isdigit():
			metadata.write_metadata(file, found_songs[int(actionable_input)])
		if actionable_input == "e":
			isrc = input("ISRC: ")
			data.isrc = isrc
			metadata.write_metadata(file, data)