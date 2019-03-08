# A spotify API wrapper based off of code from github.com/bspammer/spotify_cava_colors
# Author: David Haas
# Date: 3/7/19

import requests
import os
import time
# to view headers https://onlinecurl.com/

FILE_PATH = os.path.realpath(__file__)[:os.path.realpath(__file__).rfind("\\")]
REFRESH_TOKEN_PATH = FILE_PATH + "/auth/refresh_token"
ACCESS_TOKEN_PATH = FILE_PATH + "/auth/access_token"
APP_CREDENTIALS_PATH = FILE_PATH + "/auth/app_credentials"


class SpotifyAPI:
    GET = requests.get
    POST = requests.post

    PREFIX = "https://api.spotify.com/v1"
    CURRENTLY_PLAYING = {"url": PREFIX + "/me/player/currently-playing", "method": GET}
    NEW_TOKEN = {"url": "https://accounts.spotify.com/api/token", "method": POST}

    def __init__(self):
        print(FILE_PATH)
        try:
            with open(ACCESS_TOKEN_PATH) as f:
                self.access_token = f.read().replace("\n", "")
        except IOError:
            with open(ACCESS_TOKEN_PATH, "w") as f:
                f.write("")
            self.access_token = ""
        with open(REFRESH_TOKEN_PATH) as f:
            self.refresh_token = f.read().replace("\n", "")
        with open(APP_CREDENTIALS_PATH) as f:
            credentials = f.read().replace("\n", "")
            self.client_id, self.client_secret = credentials.split(":")

    def make_request(self, endpoint, extra={}):
        url = endpoint["url"]
        method = endpoint["method"]
        print("Making request to '%s'..." % url)
        headers = {
                "Authorization": "Bearer %s" % self.access_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
                }
        if method == self.POST:
            if endpoint == self.NEW_TOKEN:
                headers.pop("Authorization")
            r = method(url, data=extra, headers=headers)
        else:
            r = method(url, params=extra, headers=headers)

        # Obey rate limiting
        if r.status_code == 429:
            backoff_time = int(r.headers["Retry-After"])
            print("Hit rate limit, sleeping for %d seconds..." % backoff_time)
            time.sleep(backoff_time)
            return self.make_request(endpoint, extra)
        print(r)
        json = r.json()
        if "error" in json:
            if endpoint != self.NEW_TOKEN:
                token_extras = {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": self.refresh_token,
                        "grant_type": "refresh_token"
                        }
                token_r = self.make_request(self.NEW_TOKEN, extra=token_extras)
                self.access_token = token_r["access_token"]
                with open(ACCESS_TOKEN_PATH, "w") as f:
                    f.write(self.access_token + "\n")
                return self.make_request(endpoint, extra)
            else:
                print("Error, could not get new access token:\n" + str(r.json()))
                exit()
        else:
            return json


    def get_analysis(self, song_id):
        auth = 'BQBP6mTSa2nH8M873L0m5GSYg2bhtDO5UWwg5LWg44Shq2DpGNI5i8jQGE4LlnJCmPoqFQDwf7pda7V6w0y0lBQAmkQHTLmxPz4Zgeyk2avorvB2LtSec6xs3YYKHmE-lQRKIBuSiLbin22ObD0M'

        url = 'https://api.spotify.com/v1/audio-analysis/' + id
        headers = {'Authorization': 'Bearer ' + auth,
                   'Content-Type' : 'application/json',
                   'Accept': 'application/json'}

        return requests.get(url=url, headers=headers).json()