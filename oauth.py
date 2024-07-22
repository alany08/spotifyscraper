from config import config
import webbrowser
from flask import Flask, request, redirect, url_for
import requests
import base64
import sys
import os
import signal

app = Flask(__name__)

@app.route('/')
def home():
    code = request.args.get("code")
    if code:
        print(f"Authorization code received: {code}")
        get_user_token(code)
        return "Success, you may now close this window"
    else:
        print("Failed to retrieve authorization code.")
        return "Failed to retrieve authorization code."

def get_user_token(code):
    client_id = config["spotify_client_id"]
    client_secret = config["spotify_client_secret"]
    if not client_id or not client_secret:
        raise ValueError("Client ID and Client Secret must be set")

    # Constructing the base64 encoded credentials
    credentials = f"{client_id}:{client_secret}"
    base64_credentials = base64.b64encode(credentials.encode("ascii")).decode("ascii")

    # Making the POST request
    print(f"Exchanging code: {code}")
    result = requests.post("https://accounts.spotify.com/api/token", data={
        "code": code,
        "redirect_uri": "http://localhost:8081",
        "grant_type": "authorization_code"
    }, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {base64_credentials}"
    })

    response_json = result.json()
    print("Response from Spotify:", response_json)  # Debug print the response

    with open("tmp/spotifytoken.txt", "w") as file:
        try:
            file.write(response_json["access_token"])
        except KeyError:
            print("Failed to retrieve access token.")
            file.write("FAILED TO GET SPOTIFY TOKEN")
    #Exit the server
    os.kill(os.getpid(), signal.SIGINT)

def begin():
    global app
    # Ensure the tmp directory exists
    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    auth_url = f"https://accounts.spotify.com/authorize?client_id={config['spotify_client_id']}&redirect_uri=http://localhost:8081&response_type=code&show_dialog=false"
    print(f"Opening browser with URL: {auth_url}")
    webbrowser.open(auth_url)
    app.run(host='localhost', port=8081)