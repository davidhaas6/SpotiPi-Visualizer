# https://github.com/rpi-ws281x/rpi-ws281x-python
# https://circuitpython.readthedocs.io/projects/neopixel/en/latest/
#https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/

from song import SongFeature, FeaturedSong
import neopixel
import colorsys
from math import floor


# Coordinates between the Spotify Coordinator, the LEDs, and the LightShow
class LEDCoordinator:

    def __init__(self, led_strip):
        self.leds = led_strip
        self.show = None
        self.song = None
        self.last_idx = -1

    
    def build_show(self, featured_song):
        print("Building show for:", featured_song)
        self.show = LightShow(featured_song, self.leds.n)
        print("Built!")
        print("Showlen:", len(self.show.show), "song len:", len(featured_song))
        print(self.show.show[0:2])


    def play_segment(self, time):
        #print(time)
        self.set_leds(self.show[time])

    def set_leds(self, arr):

        for i in range(0, self.leds.n):
            try:
                self.leds[i] = arr[i]
            except Exception as e:
                print(arr[i])
                print(e)

        self.leds.show()


class LightShow:
    # https://www.rapidtables.com/web/color/color-wheel.html
    def __init__(self, featured_song, num_leds):
        self.featured_song = featured_song
        self.num_leds = num_leds
        self.show = list()

        vol_std = featured_song.volume_std
        vol_med = featured_song.volume_med
        self.volume_range = (vol_med - 2 * vol_std, vol_med, vol_med + vol_std)  # min, medium, max (ish)
        #print(self.volume_range)

        MINOR_HUE_CENTER = 250
        MAJOR_HUE_CENTER = 70
        mode = self.featured_song.mode

        self.hue_offset = MINOR_HUE_CENTER if mode == 0 else MAJOR_HUE_CENTER
        self.MOVEMENT_RANGE = 90  # The LEDS can vary +- 120 degrees from the center

        self._build()


    def _build(self, style=None):
        for feat in self.featured_song:
            self.show.append(self.feature_to_led(feat))


    def feature_to_led(self, feature):
        hue = self._pitch_to_hue(feature.pitches)
        sat = self._timbre_to_saturation(feature.timbre)
        val = self._volume_to_value(feature.volume)

        rgb = self._hsv_to_rgb(hue,sat,val)
        leds = [rgb] * self.num_leds
        return leds

    def _pitch_to_hue(self, pitches):
        val = max(pitches)
        note = pitches.index(val)

        if note > 5:
            movement_factor = (note - 12)/6
        else:
            movement_factor = note/5

        movement = movement_factor * val * self.MOVEMENT_RANGE
        hue = self.hue_offset + movement

        # Adjust for out of bound hues
        if hue < 0:
            hue+= 360
        elif hue > 360:
            hue -= 360

        return hue

    def _volume_to_value(self, volume):
        if volume < self.volume_range[1]:
            temp = (volume - self.volume_range[0] ) / ( self.volume_range[1] - self.volume_range[0])
            return temp * 128
        else:
            temp = (volume - self.volume_range[1]) / (self.volume_range[2] - self.volume_range[1])
            return temp * 128 + 127

    def _timbre_to_saturation(self, timbre):
        # uses flatness and brightness components
        sat = 128
        return min(sat, 255)

    def _hsv_to_rgb(self, h,s,v):
        r,g,b = colorsys.hsv_to_rgb(h/360,s/255,v/255)
        r = int(r * 255)
        g = int(g * 255)
        b =int(b * 255)
        return min(r,255), min(g,255), min (b,255)

    def __getitem__(self, time):
        if time >= self.featured_song.duration_ms:
            return None

        idx = int(floor(time / self.featured_song.period))
        return self.show[idx]
