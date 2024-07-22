#Make requests to spotify api
from config import config
from track import Track
import requests
import time
import urllib.parse
import pickle

_headers = {
        "User-Agent": "SongOrganizer/0.1 Python/3",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Authorization": "Bearer " + config["spotify_api_bearer"],
}

past_api_requests = [
	time.time()
]

cached_requests = {
	"url": "responseobject"
}
try:
	with open("apicache.pickle", "rb") as f:
		cached_requests = pickle.load(f)
except Exception:
	print("Couldn't load response cache")

#90 requests every 30 seconds

def get_request(url, headers = {}, ratelimited = False):
	global past_api_requests
	global cached_requests
	global config
	global _headers
	new_past_api_requests = []

	try:
		if cached_requests[url]:
			print("Found cached request for", url)
			return cached_requests[url]
	except:
		pass

	time.sleep(0.25)

	for i in range(len(past_api_requests)):
		if time.time() - past_api_requests[i] < config["ratelimit_duration"]:
			new_past_api_requests.append(past_api_requests[i])
	past_api_requests = new_past_api_requests

	if len(past_api_requests) > config["ratelimit_limit"]:
		print(f"Hitting ratelimit ({config["ratelimit_limit"]}/{config["ratelimit_duration"]}s), waiting 3 seconds and trying again")
		time.sleep(3)
		return get_request(url, headers = headers)

	past_api_requests.append(time.time())
	response = requests.get(url, headers = headers)
	if response.status_code == 429:
		if ratelimited:
			print("Getting multiple 429's in a row, waiting 10 minutes")
			time.sleep(300)
		else:
			print("Got 429 on response, waiting 60 seconds")
			time.sleep(60)
		return get_request(url, headers = headers, ratelimited = True)
	if response.status_code == 401:
		key = input("Authentication key expired! Please enter another one: ")
		config["spotify_api_bearer"] = key
		_headers = {
		        "User-Agent": "SongOrganizer/0.1 Python/3",
		        "Accept": "*/*",
		        "Accept-Language": "en-US,en;q=0.5",
		        "Authorization": "Bearer " + config["spotify_api_bearer"],
		}
		return get_request(url, headers = _headers)
	if response.status_code != 200:
		print("Got unknown error:", response.status_code, "not retrying")
		raise RuntimeError(response.status_code)

	cached_requests[url] = response
	pickle.dump(cached_requests, open("apicache.pickle", "w"))
	return response

def get_playlist_tracks(playlistID: str):
	global headers
	nexturl = f"{config["spotify_api_root"]}/playlists/{playlistID}/tracks?offset=0&limit=50"
	playlist_items = []
	while nexturl:
		response = get_request(nexturl, headers = _headers).json()
		nexturl = response["next"]
		for track in response["items"]:
			playlist_items.append(Track(TrackObject = track["track"]))
	return playlist_items

def get_playlist_name(playlistID: str):
	return get_request(f"{config["spotify_api_root"]}/playlists/{playlistID}", headers=headers).json()["name"]

def download_image(url, path):
	data = get_request(url).content
	with open(path, "wb") as file:
		file.write(data)

def search_for_track(name = "", artist = "", isrc = None):
	global headers

	try:
		int(name.split(" ")[0])
		name = " ".join(name.split(" ")[1:])
	except:
		pass

	for file_ext in config["accepted_file_extensions"]:
		if name.endswith("." + file_ext):
			name = name[:-(len(file_ext) + 1)]

	name = urllib.parse.quote(name, safe="")
	artist = urllib.parse.quote(artist, safe="")

	if not isrc:
		result = get_request(
			f"{config["spotify_api_root"]}/search?q=name:{name}{f" artist:{artist}" if artist else ""}&type=track",
			headers = _headers
		).json()
	else:
		result = get_request(
			f"{config["spotify_api_root"]}/search?q=isrc:{isrc}&type=track&limit=3&offset=0",
			headers = _headers
		).json()

	return Track(TrackObject = result["tracks"]["items"][0])