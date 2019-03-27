import spotipy_fork
from spotipy_fork import util
from song import FeaturedSong, Song
from led import LEDCoordinator
from multiprocessing import Process
import time
from pprint import pprint
import numpy as np


def _generate_token():
    c_id = '0ffd86016ea04c7094adb889672d8bda'
    secret = '6891793ab2a74e57aa86399b8982d3e4'
    username = 'davidhaas123'
    scope = 'user-read-playback-state'
    return util.prompt_for_user_token(username=username, client_id=c_id, client_secret=secret, scope=scope,
                                      redirect_uri='http://example.com/callback/')


class SpotifyCoordinator:
    #TODO: Thread external processes such as building the show and fetching songs

    def __init__(self, led_strip, analysis_freq=100, update_freq=None):
        self.led_coord = LEDCoordinator(led_strip)
        self.spotify = spotipy_fork.Spotify(auth=_generate_token())
        self.analysis_period = (1/analysis_freq) * 1000
        self.play_info = None
        self.song = None
        self.featured_song = None

        if update_freq is None:
            # Update the LEDS at twice the frequency of the segments to be safe
            self.update_period = (1/(analysis_freq*2)) * 1000
        else:
            self.update_period = (1/update_freq) * 1000

        self.coordinator = Process(target=self._coordinator_worker)  # ,args=(self,)

    def fetch_song(self, do_analysis=True):
        self.song = None
        print("Fetching song...")
        self.play_info = self.spotify.current_playback()

        if self.play_info is not None and self.play_info["item"] is not None:
            song_id = self.play_info["item"]["id"]
            name = self.play_info["item"]["name"]
            duration = self.play_info["item"]["duration_ms"]

            if do_analysis:
                analysis = self.spotify.audio_analysis(song_id)
                features = self.spotify.audio_features([song_id])[0]

                print("Building featured song...")
                self.featured_song = FeaturedSong(
                    name, song_id, duration, features, analysis, self.analysis_period)
                self.song = self.featured_song

                vols = self.featured_song.volume_arr
                print(np.std(vols), np.median(vols), np.mean(vols), np.max(vols))
                print(self.featured_song.loudness)
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
        if not self.coordinator.is_alive():
            try:
                self.coordinator.start()
                return True
            except Exception as e:
                print(e)
                return False
        return False


    def _coordinator_worker(self):
        start_time = -1
        while True:
            while not self.is_playing():
                time.sleep(0.1)
                start_time = time.time()
                self.fetch_song()


            self.led_coord.build_show(self.featured_song)

            progress = self.play_info["progress_ms"]
            duration = self.song.duration_ms

            last_seg_t = time.time()
            self.led_coord.play_segment(progress)
            while progress < duration:

                if start_time > (last_seg_t + self.update_period / 1000):
                    last_seg_t = time.time()
                    self.led_coord.play_segment(progress)

                progress += (time.time() - start_time) * 1000
                start_time = time.time()


if __name__ == '__main__':
    sc = SpotifyCoordinator(None)
    sc.begin()