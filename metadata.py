from spotify import download_image
from track import Track
from mutagen.id3 import APIC, error, ID3
from mutagen.mp3 import EasyMP3, MP3
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4, MP4Cover
from mutagen import File
import os
import sys

def write_metadata(filepath, track: Track):
	f = get_metadata(filepath)
	if f.isrc != track.isrc:
		print("Modifying ISRC!", track, f)
		sys.exit()

	try:
		thumbnail_path = track.isrc + ".png"
		download_image(track.cover_image_url, thumbnail_path)
	except:
		thumbnail_path = None

	audio = None

	if filepath.endswith(".mp3"):
		if thumbnail_path:
			audio = MP3(filepath)
			with open(thumbnail_path, "rb") as f:
				data = f.read()
			#add thumbnail
			audio.tags.add(
				APIC(
						encoding=0,
						mime="image/png",
						type=3,
						desc=u"Cover",
						data=data
				)
			)

		audio = EasyMP3(filepath)

		#add title
		audio["title"] = track.name
		#add artist
		audio["artist"] = track.artists
		#add disc number
		audio["tracknumber"] = track.disc_no + "/" + track.totaltracks
		#add album
		audio["album"] = track.album
		#add release date
		audio["date"] = track.release_date
		#add isrc
		audio["isrc"] = track.isrc
		#add genre
		audio["genre"] = track.genres

		audio.save()

	if filepath.endswith(".m4a"):
		audio = MP4(filepath)

		if thumbnail_path:
			#add thumbnail
			with open(thumbnail_path, "rb") as f:
				audio["covr"] = [
					MP4Cover(f.read(), imageformat=MP4Cover.FORMAT_PNG)
				]

		#THESE ARE FROM https://mutagen.readthedocs.io/en/latest/api/mp4.html
		#add title
		audio["\xa9nam"] = track.name
		#add artist
		audio["\xa9ART"] = track.artists
		#add disc number#add album
		audio["\xa9alb"] = track.album
		#add album artists
		audio["aART"] = track.albumartists #!!!! Not supported in ID3
		#add release date
		audio["\xa9day"] = track.release_date
		#add genre
		audio["\xa9gen"] = track.genres
		#add track num of total tracks
		audio["trkn"] = audio["disk"] = [(int(track.disc_no), int(track.totaltracks))]
		#ISRC, Spotify ID as comment, because not supported by itself
		audio["\xa9cmt"] = f"ISRC:{track.isrc}\nSpotify ID:{track.spotify_id}"

		audio.save()

	if filepath.endswith(".flac"):
		audio = FLAC(filepath)

		if thumbnail_path:
			#add thumbnail
			image = Picture()
			image.type = 3
			mime = "image/png"
			image.desc = "front cover"
			with open(thumbnail_path, "rb") as f:
				image.data = f.read()
			audio.add_picture(image)

		#add title
		audio["title"] = track.name
		#add artist
		audio["artist"] = track.artists
		#add disc number
		audio["tracknumber"] = track.disc_no
		#add spotify id
		audio["spotifyid"] = track.spotify_id #!!!! Not supported in ID3
		#add album
		audio["album"] = track.album
		#add album artists
		audio["albumartists"] = track.albumartists #!!!! Not supported in ID3
		#add release date
		audio["date"] = track.release_date
		#add isrc
		audio["isrc"] = track.isrc
		#add total tracks
		audio["tracktotal"] = track.totaltracks #!!!! Not supported in ID3
		#add genres
		audio["genre"] = track.genres

		audio.save()

	os.remove(thumbnail_path)

	if not audio:
		raise TypeError("Filepath given was not an recognized audio format (mp3, m4a, flac). If this is an audio format, consider adding it in metadata.py")


def get_metadata(filepath):
	
	audio = None

	if filepath.endswith(".mp3"):
		track = Track()
		audio = EasyMP3(filepath)
		#add title
		try:
			track.name = audio["title"][0]
		except Exception:
			pass
		try:
			track.artists = audio["artist"]
		except Exception:
			pass
		try:
			track.disc_no = audio["tracknumber"][0]
		except Exception:
			pass
		try:
			track.album = audio["album"][0]
		except Exception:
			pass
		try:
			track.release_date = audio["date"][0]
		except Exception:
			pass
		try:
			track.isrc = audio["isrc"][0]
		except Exception:
			pass
		try:
			track.genres = audio["genre"]
		except Exception:
			pass

	if filepath.endswith(".m4a"):
		track = Track()
		audio = MP4(filepath)

		#add title
		try:
			track.name = audio["\xa9nam"][0]
		except Exception:
			pass
		try:
			track.artists = audio["\xa9ART"]
		except Exception:
			pass
		try:
			track.disc_no, track.totaltracks = audio["trkn"][0]
		except Exception:
			pass
		try:
			track.album = audio["\xa9alb"][0]
		except Exception:
			pass
		try:
			track.release_date = audio["\xa9day"][0]
		except Exception:
			pass
		try:
			track.isrc = audio["\xa9cmt"].split("\n")[0].split(":")[1]
		except Exception:
			try:
				track.isrc = audio["xid "][0].split(":")[-1]
			except Exception:
				pass
		try:
			track.spotify_id = audio["\xa9cmt"].split("\n")[1].split(":")[1]
		except Exception:
			pass
		try:
			track.genres = audio["\xa9gen"]
		except Exception:
			pass
		try:
			track.albumartists = audio["aART"]
		except Exception:
			pass

	if filepath.endswith(".flac"):
		track = Track()
		audio = FLAC(filepath)

		#add title
		try:
			track.name = audio["title"][0]
		except Exception:
			pass
		try:
			track.artists = audio["artist"]
		except Exception:
			pass
		try:
			track.disc_no = audio["tracknumber"][0]
		except Exception:
			pass
		try:
			track.totaltracks = audio["tracktotal"][0]
		except Exception:
			pass
		try:
			track.album = audio["album"][0]
		except Exception:
			pass
		try:
			track.release_date = audio["date"][0]
		except Exception:
			pass
		try:
			track.isrc = audio["isrc"][0]
		except Exception:
			pass
		try:
			track.spotify_id = audio["spotifyid"]
		except Exception:
			pass
		try:
			track.genres = audio["genre"]
		except Exception:
			pass
		try:
			track.albumartists = audio["albumartists"]
		except Exception:
			pass

	#if not audio:
	#	raise TypeError("Filepath given was not an recognized audio format (mp3, m4a, flac). If this is an audio format, consider adding it in metadata.py")

	#sometimes disc_no is num/num
	try:
		int(track.disc_no)
	except Exception:
		try:
			track.totaltracks = track.disc_no.split("/")[1]
			track.disc_no = track.disc_no.split("/")[0]
		except Exception:
			pass

	try:
		if len(track.artists) == 1 and ("," in track.artists[0] or "&" in track.artists[0]):
			track.artists = track.artists[0].split(", ")
			track.artists = track.artists[0].split(" & ")
	except Exception:
		pass

	return track

def get_bitrate(filepath):
	audio = None
	if filepath.endswith("mp3"):
		audio = MP3(filepath)
	if filepath.endswith("m4a"):
		audio = MP4(filepath)
	if filepath.endswith("flac"):
		audio = FLAC(filepath)
	if not audio:
		raise TypeError("Invalid file extension. Please consider adding support for this audio type if you think this is a valid audio type")
	return audio.info.bitrate