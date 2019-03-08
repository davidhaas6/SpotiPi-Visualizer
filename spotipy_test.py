import spotipy_fork
from spotipy_fork import util
from pprint import pprint
from song import FeaturedSong
import math

# https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-analysis/

c_id = '0ffd86016ea04c7094adb889672d8bda'
secret = '6891793ab2a74e57aa86399b8982d3e4'
username = 'davidhaas123'
scope = 'user-read-playback-state'
token = util.prompt_for_user_token(username=username, client_id=c_id, client_secret=secret, scope=scope,
                                   redirect_uri='http://example.com/callback/')
sp = spotipy_fork.Spotify(auth=token)


curr = sp.current_playback()
progress = curr["progress_ms"]
is_playing = curr["is_playing"]
song_id = curr["item"]["id"]
name = curr["item"]["name"]
duration = curr["item"]["duration_ms"]
print(progress, is_playing, song_id, name, duration)

analysis = sp.audio_analysis(song_id)
spotify_segments = analysis["segments"]


features = sp.audio_features([song_id])
print(features)

def ceil_ones(num):
    return math.ceil(num/10) * 10



