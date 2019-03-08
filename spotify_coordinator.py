import spotipy_fork
from spotipy_fork import util
from song import FeaturedSong, Song


def _generate_token():
    c_id = '0ffd86016ea04c7094adb889672d8bda'
    secret = '6891793ab2a74e57aa86399b8982d3e4'
    username = 'davidhaas123'
    scope = 'user-read-playback-state'
    return util.prompt_for_user_token(username=username, client_id=c_id, client_secret=secret, scope=scope,
                                      redirect_uri='http://example.com/callback/')

class SpotifyCoordinator:
    def __init__(self, analysis_freq=100):
        self.spotify = spotipy_fork.Spotify(auth=_generate_token())
        self.play_info = None
        self.song = None
        self.featured_song = None
        self.analysis_period = (1/analysis_freq) * 1000

    def fetch_song(self, do_analysis=True):
        self.play_info = self.spotify.current_playback()
        song_id = self.play_info["item"]["id"]
        name = self.play_info["item"]["name"]
        duration = self.play_info["item"]["duration_ms"]

        if do_analysis:
            analysis = self.spotify.audio_analysis(song_id)
            features = self.spotify.audio_features([song_id])

            self.featured_song(name, song_id, duration, analysis, features, self.analysis_period)
            self.song = self.featured_song
        else:
            self.song = Song(name, song_id, duration)


    def is_playing(self):
        return self.play_info['is_playing']

    def begin(self):





curr = sp.current_playback()
is_playing = curr["is_playing"]
if is_playing:
    progress = curr["progress_ms"]
    song_id = curr["item"]["id"]
    name = curr["item"]["name"]
    duration = curr["item"]["duration_ms"]
    print(progress, is_playing, song_id, name, duration)

    fs = FeaturedSong(duration, analysis)

    analysis = sp.audio_analysis(song_id)
    spotify_segments = analysis["segments"]



