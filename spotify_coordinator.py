import spotipy_fork
from spotipy_fork import util
from song import FeaturedSong, Song
import threading
import time


def _generate_token():
    c_id = '0ffd86016ea04c7094adb889672d8bda'
    secret = '6891793ab2a74e57aa86399b8982d3e4'
    username = 'davidhaas123'
    scope = 'user-read-playback-state'
    return util.prompt_for_user_token(username=username, client_id=c_id, client_secret=secret, scope=scope,
                                      redirect_uri='http://example.com/callback/')


class SpotifyCoordinator:
    THREAD_NAME = 'watchdog'

    def __init__(self, analysis_freq=100):
        self.spotify = spotipy_fork.Spotify(auth=_generate_token())
        self.play_info = None
        self.song = None
        self.featured_song = None
        self.analysis_period = (1/analysis_freq) * 1000

        self.watchdog = threading.Thread(
            name=SpotifyCoordinator.THREAD_NAME, target=self._watchdog_worker)

    def fetch_song(self, do_analysis=True):
        self.song = None
        self.play_info = self.spotify.current_playback()

        if self.play_info is not None and self.play_info["item"] is not None:
            song_id = self.play_info["item"]["id"]
            name = self.play_info["item"]["name"]
            duration = self.play_info["item"]["duration_ms"]

            if do_analysis:
                analysis = self.spotify.audio_analysis(song_id)
                features = self.spotify.audio_features([song_id])

                self.featured_song = FeaturedSong(
                    name, song_id, duration, analysis, features, self.analysis_period)
                self.song = self.featured_song
            else:
                self.song = Song(name, song_id, duration)
                self.featured_song = None

            return True
        else:
            return False

    def is_playing(self):
        if self.play_info is None:
            return False

        return self.play_info['is_playing']

    def begin(self):
        if not self.watchdog.is_alive():
            try:
                self.watchdog.start()
                return True
            except Exception as e:
                print(e)
                return False
        return False


    def _watchdog_worker(self):
        while True:
            while not self.is_playing():
                self.fetch_song()
                time.sleep(0.1)

            start_time = time.time()
            progress = self.play_info["progress_ms"]
            duration = self.song.duration_ms

            while progress < duration:
                seg = self.featured_song.get_segment(progress)
                


# class SpotifyWatchdog(threading.Thread):
#     # https://www.tutorialspoint.com/python3/python_multithreading.htm
#     # https://docs.python.org/3/library/threading.html
#     def __init__(self, thread_id, name, coordinator):
#         threading.Thread.__init__(self)
#
#         self.thread_id = thread_id
#         self.name = name
#         self.master = coordinator
#
#     def run(self):
#         print("Starting spotify watchdog", self.name)
#         pass
#
#     def watch(self):
#         while not self.master.is_playing():
#             self.master.fetch_song()
#             time.sleep(0.1)
#
#         if self.master.is_playing():
#             start_time = time.time()
#             progress = self.master.play_info["progress_ms"]
#             duration = self.master.song.duration_ms
#             cs = self.master.featured_song.get_segment()
