#data structure for a track

class Track:
	def __init__(self, TrackObject = None):
		self.name = ""
		self.artists = []
		self.disc_no = "0"
		self.spotify_id = ""
		self.album = ""
		self.albumartists = []
		self.release_date = ""
		self.cover_image_url = ""
		self.isrc = ""
		self.genres = []
		self.totaltracks = "0"
		if TrackObject:
			self.name = TrackObject["name"][:64] #truncate names that are too long
			for artist in TrackObject["artists"]:
				self.artists.append(artist["name"])
				try:
					self.genres.append(artist["genre"])
				except:
					print("No genres for artist", artist["name"])
			self.disc_no = str(TrackObject["disc_number"])
			self.spotify_id = TrackObject["id"]
			self.album = TrackObject["album"]["name"]
			for artist in TrackObject["album"]["artists"]:
				self.albumartists.append(artist["name"])
			self.release_date = TrackObject["album"]["release_date"]
			self.cover_image_url = TrackObject["album"]["images"][0]["url"]
			self.isrc = TrackObject["external_ids"]["isrc"]
			self.totaltracks = str(TrackObject["album"]["total_tracks"])