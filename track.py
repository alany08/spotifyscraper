#data structure for a track
import json

class Track:
	def __init__(self, TrackObject = None):
		self.name = ""
		self.artists = []
		self.disc_no = "0"
		self.track_no = "0"
		self.spotify_id = ""
		self.album = ""
		self.albumartists = []
		self.release_date = ""
		self.cover_image_url = ""
		self.isrc = ""
		self.genres = []
		self.totaltracks = "0"
		if TrackObject:
			self.overwrite_with_spotify(TrackObject)
	def __str__(self):
		return json.dumps({
			"name": self.name,
			"artists": self.artists,
			"disc_no": self.disc_no,
			"spotify_id": self.spotify_id,
			"album": self.album,
			"albumartists": self.albumartists,
			"release_date": self.release_date,
			"cover_image_url": self.cover_image_url,
			"isrc": self.isrc,
			"genres": self.genres,
			"totaltracks": self.totaltracks
		}, indent=4)
	def overwrite_with_spotify(self, TrackObject):
		self.name = TrackObject["name"]
		for artist in TrackObject["artists"]:
			self.artists.append(artist["name"])
			try:
				self.genres.append(artist["genre"])
			except:
				pass
				# print("No genres for artist", artist["name"])
		self.disc_no = str(TrackObject["disc_number"])
		self.track_no = str(TrackObject["track_number"])
		self.spotify_id = TrackObject["id"]
		self.album = TrackObject["album"]["name"]
		for artist in TrackObject["album"]["artists"]:
			self.albumartists.append(artist["name"])
		self.release_date = TrackObject["album"]["release_date"]
		self.cover_image_url = TrackObject["album"]["images"][0]["url"]
		self.isrc = TrackObject["external_ids"]["isrc"]
		self.totaltracks = str(TrackObject["album"]["total_tracks"])