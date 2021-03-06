import time
from math import floor
import numpy as np

# https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-analysis/

class Song:
    def __init__(self, name, song_id, duration_ms, key=None, mode=None):
        self.name = name
        self.spotify_id = song_id
        self.duration_ms = duration_ms
        self.key = key
        self.mode = mode

    def __str__(self):
        pitch_class = ['C', 'C#/Db', 'D', 'D#/Eb', 'E', 'F', 'F#/Gb', 'G', 'G#/Ab', 'A', 'A#/Bb', 'B']
        modalities = ['Major', 'Minor']

        name_time = self.name + " - " + str(round(self.duration_ms/1000,1)) + "s - "
        pitch_mode = "Key: " + pitch_class[self.key] + ' - Modality: ' + modalities[self.mode]

        return name_time + pitch_mode


class SongFeature:
    def __init__(self, timbre, pitches, max_loudness, duration_ms):
        self.duration = duration_ms
        self.timbre = timbre
        self.pitches = pitches
        self.volume = max_loudness
        self.primary_pitch = pitches.index(max(pitches))
        self.primary_timbre = timbre.index(max(timbre))


class FeaturedSong(Song):
    # Breaks up song into X ms brackets where each bracket has a SongFeature element describing that time period
    def __init__(self, name, song_id, duration_ms, features, analysis, segment_period=10):
        #Idea: Cache sound features locally?
        self.period = segment_period
        self.song_segments = [None] * round(duration_ms/self.period)
        self.segments = analysis['segments']
        self.duration_ms = duration_ms

        self.features = features
        self.key = features['key']
        self.mode = features['mode']
        self.tempo = features['tempo']
        self.loudness = features['loudness']
        self.danceability = features['danceability']

        self.volume_arr = np.zeros(len(self.song_segments))
        self._build_feature_array()

        self.volume_std = np.std(self.volume_arr)
        self.volume_med = np.median(self.volume_arr)

        super().__init__(name, song_id, duration_ms, self.key, self.mode)

    def _build_feature_array(self):
        seg_index = 0

        i = 0
        while i < len(self.song_segments):
            cur_seg = self.segments[seg_index]
            seg_start = int(cur_seg['start'] * 1000)
            seg_end = int(seg_start + cur_seg['duration'] * 1000)

            bracket_start = int(i * self.period)
            bracket_end = int((i + 1) * self.period)

            # If they intersect
            if bracket_start <= seg_end and seg_start <= bracket_end:
                #TODO: Add support for multiple features within a single bracket
                sf = SongFeature(cur_seg['timbre'], cur_seg['pitches'], cur_seg['loudness_max'],
                                duration_ms=self.period)
                self.song_segments[i] = sf
                self.volume_arr[i] = sf.volume
                i+=1
            else:
                # Check the next segment
                #i-=1
                seg_index+=1

    def get_segment(self, cur_time):
        if cur_time >= self.duration_ms:
            return False

        idx = int(floor(cur_time/self.period))
        return self.song_segments[idx]

    def time_to_index(self, cur_time):
        if cur_time >= self.duration_ms:
            return -1

        return int(floor(cur_time/self.period))

    def __getitem__(self, index):
        return self.song_segments[index]

    def __len__(self):
        return len(self.song_segments)

    def __iter__(self):
        return iter(self.song_segments)
