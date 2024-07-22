from config import config
import webbrowser
from flask import Flask, request, redirect, url_for
import requests
from config import config
import base64
import sys

app = Flask(__name__)

@app.route('/')
def home():
    code = request.args.get("code")
    get_user_token(code)
    return "Success, you may now close this window"

def get_user_token(code):
    client_id = config["spotify_client_id"]
    client_secret = config["spotify_client_secret"]
    if not client_id or not client_secret:
        raise ValueError("Client ID and Client Secret must be set")

    # Constructing the base64 encoded credentials
    credentials = f"{client_id}:{client_secret}"
    base64_credentials = base64.b64encode(credentials.encode("ascii")).decode("ascii")

    # Making the POST request
    result = requests.post("https://accounts.spotify.com/api/token", data={
        "code": code,
        "redirect_uri": "http://localhost:8081",  # Note the change from redirect_url to redirect_uri
        "grant_type": "authorization_code"
    }, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {base64_credentials}"
    })
    with open("tmp/spotifytoken.txt", "w") as file:
    	file.write(result.json()["access_token"])
    sys.exit()

def begin():
	global app
	webbrowser.open(f"https://accounts.spotify.com/authorize/?client_id={config["spotify_client_id"]}&redirect_uri=http://localhost:8081&response_type=code&show_dialog=false")
	app.run(host='localhost', port=8081)