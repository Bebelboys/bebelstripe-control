import board
import neopixel
import time
from math import cos

from options import *


class LEDWall:
    def __init__(self):
        self.num_rows = 44
        self.num_columns = 8
        self.num_pixel = self.num_rows * self.num_columns
        self.pixel_pin = board.D18
        self.pixel_type = neopixel.GRB
        self.pixels = neopixel.NeoPixel(pin=self.pixel_pin, n=self.num_pixel, brightness=1.0, auto_write=False,
                                        pixel_order=self.pixel_type)
        self.oldValue = [0, 0, 0, 0, 0, 0, 0, 0]
        self.dotFallingRate = 0

    def music_spectrum(self, shared_vars):
        self.sinus(iterations=1)
        while True:
            self.falling_dot(shared_vars.music_spectrum_levels)
            self.refresh_spectrum(shared_vars.music_spectrum_levels)

    def refresh_spectrum(self, spectrum_levels):
        for column in range(0, self.num_columns):
            # 1: Statt > 43 lieber auf > self.num_rows - 1 prüfen? 
            # 2: Eigentlich wärs schöner wenn FFT.py den Check/Korrektur durchführt
            if spectrum_levels[column] > 43:
                spectrum_levels[column] = 43
            for neglevel in range(0, self.num_rows - spectrum_levels[column]):
                self.pixels[self.num_rows * column + self.num_rows - 1 - neglevel] = (0, 0, 0)
            for level in range(0, spectrum_levels[column]):
                self.pixels[self.num_rows * column + level] = levelColor
            self.pixels[self.num_rows * column + self.oldValue[column]] = dotColor
        self.pixels.show()

    def falling_dot(self, spectrum_levels):
        for column in range(0, self.num_columns):
            if spectrum_levels[column] > 43:
                spectrum_levels[column] = 43
            if self.oldValue[column] <= spectrum_levels[column]:
                self.oldValue[column] = spectrum_levels[column]
            elif self.oldValue[column] > 0 and self.dotFallingRate > 1:
                self.oldValue[column] -= 1
        if self.dotFallingRate > 1:
            self.dotFallingRate = 0
        else:
            self.dotFallingRate += 1

    def sinus(self, iterations):
        value = [0, 0, 0, 0, 0, 0, 0, 0]
        for index in range(0, iterations):
            for c in range(0, 25):
                for i in range(0, 8):
                    value[i] = self.translate(cos(i * 6.24 / 6 + c) * 100, -100, 100, 10, 34)
                    self.pixels[int(value[i] + i * self.num_rows)] = (0, 0, 200)
                self.pixels.show()
                time.sleep(0.05)
                self.pixels.fill((0, 0, 0))
                self.pixels.show()

    @staticmethod
    def translate(value, left_min, left_max, right_min, right_max):
        # Figure out how 'wide' each range is
        left_span = left_max - left_min
        right_span = right_max - right_min
        # Convert the left range into a 0-1 range (float)
        value_scaled = float(value - left_min) / float(left_span)
        # Convert the 0-1 range into a value in the right range.
        return right_min + (value_scaled * right_span)
