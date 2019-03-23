from spotify_coordinator import SpotifyCoordinator
import board
import neopixel

pixel_pin = board.D18  # RPi data pin
ORDER = neopixel.GRB  # The order of the pixel colors
num_pixels = 225
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False,
                           pixel_order=ORDER)

spot = SpotifyCoordinator(pixels)
spot.begin()