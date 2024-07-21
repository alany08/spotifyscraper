#Make requests to spotify api
from config import config
from track import Track
import requests
import time

headers = {
        "User-Agent": "SongOrganizer/0.1 Python/3",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Authorization": "Bearer " + config["spotify_api_bearer"],
}

past_api_requests = [
	time.time()
]

#90 requests every 30 seconds

def get_request(url, headers = {}):
	global past_api_requests
	new_past_api_requests = []

	time.sleep(0.25)

	for i in range(len(past_api_requests)):
		if time.time() - past_api_requests[i] < 30:
			new_past_api_requests.append(past_api_requests[i])
	past_api_requests = new_past_api_requests

	if len(past_api_requests) > 90:
		print("Hitting ratelimit (90/30s), waiting 3 seconds and trying again")
		time.sleep(3)
		return get_request(url, headers = headers)

	past_api_requests.append(time.time())
	response = requests.get(url, headers = headers)

	if response.status_code == 429:
		print("Got 429 on response, waiting 30 seconds")
		time.sleep(30)
		return get_request(url, headers = headers)
	if response.status_code != 200:
		print("Got unknown error:", response.status_code, "not retrying")
		raise RuntimeError(response.status_code)

	return response

def get_playlist_tracks(playlistID: str):
	global headers
	nexturl = f"{config["spotify_api_root"]}/playlists/{playlistID}/tracks?offset=0&limit=50"
	playlist_items = []
	while nexturl:
		response = get_request(nexturl, headers = headers).json()
		nexturl = response["next"]
		for track in response["items"]:
			playlist_items.append(Track(TrackObject = track["track"]))
	return playlist_items

print(len(get_playlist_tracks("4NcVSxlT1ZJ31GlalJGXms")))