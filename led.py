# https://github.com/rpi-ws281x/rpi-ws281x-python
# https://circuitpython.readthedocs.io/projects/neopixel/en/latest/

from song import SongFeature, FeaturedSong
#import neopixel
import colorsys


# Coordinates between the Spotify Coordinator, the LEDs, and the LightShow
class LEDCoordinator:

    def __init__(self, led_strip):
        self.leds = led_strip
        self.show = None
        self.song = None

    
    def build_show(self, featured_song):
        #TODO

        print("Building show for:", featured_song)
        pass
    
    def play_segment(self, time):
        #TODO
        print("Playing time:", time)
        pass


class LightShow:
    # https://www.rapidtables.com/web/color/color-wheel.html
    def __init__(self, featured_song):
        self.song = featured_song
        self.show = list()

    def build(self, style):
        pass

    def feature_to_led(self, segment, style):
        pass

    def hsv2rgb(self, h,s,v):
        r,g,b = colorsys.hsv_to_rgb(h/360,s/255,v/255)
        return r*255, g*255, b*255
