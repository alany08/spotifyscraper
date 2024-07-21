from spotify import download_image
from track import Track
from mutagen.id3 import APIC, error, ID3
from mutagen.mp3 import EasyMP3, MP3
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4
from mutagen import File
import os

def write_metadata(filepath, track: Track):

	thumbnail_path = track.isrc + ".png"
	download_image(track.cover_image_url, thumbnail_path)

	audio = None

	if filepath.endswith(".mp3"): #add genres and tracktotals
		audio = MP3(filepath)

		#add thumbnail
		audio.tags.add(
			APIC(
					encoding=0,
					mime="image/png",
					type=3,
					desc=u"Cover",
					data=open(thumbnail_path, "rb").read()
			)
		)
		audio.save()

		audio = EasyMP3(filepath)

		#add title
		audio["title"] = track.name
		#add artist
		audio["artist"] = track.artists
		#add disc number
		audio["tracknumber"] = track.disc_no
		#add album
		audio["album"] = track.album
		#add release date
		audio["date"] = track.release_date
		#add isrc
		audio["isrc"] = track.isrc

		audio.save()

	if filepath.endswith(".m4a"): #add cover image
		audio = MP4(filepath)

		#add thumbnail
		#asdfyhasdkjh

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
		audio["\xa9alb"] = track.release_date
		#add genre
		audio["\xa9gen"] = track.genres
		#add track num of total tracks
		audio["trkn"] = audio["disk"] = (track.disc_no, track.totaltracks)
		#ISRC, Spotify ID as comment, because not supported by itself
		audio["\xa9cmt"] = f"ISRC:{track.isrc}\nSpotify ID:{track.spotify_id}"
		audio.save()

	if filepath.endswith(".flac"):
		audio = FLAC(filepath)

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
		audio["tracktotal"] = track.totaltracks
		#add genres
		audio["genre"] = track.genres

		audio.save()

	os.remove(thumbnail_path)

	if not audio:
		raise TypeError("Filepath given was not an recognized audio format (mp3, m4a, flac). If this is an audio format, consider adding it in metadata.py")


def get_metadata(filepath):
