import board
import neopixel
import time
from math import cos
import numpy as np


class LEDWall:
    num_rows = 44
    num_columns = 8
    def __init__(self):

        self.num_pixel = LEDWall.num_rows * LEDWall.num_columns
        self.pixel_pin = board.D18
        self.pixel_type = neopixel.GRB
        self.pixels = neopixel.NeoPixel(pin=self.pixel_pin, n=self.num_pixel, brightness=1.0, auto_write=False,
                                        pixel_order=self.pixel_type)
        self.fallingDotOldValue = [0, 0, 0, 0, 0, 0, 0, 0]
        self.dotFallingRate = 0
        self.oldSpectrumLevels = np.array(8 * [0])

    def music_spectrum(self, shared_vars):
        while True:
            if shared_vars.kill_threads:
                break
            # Smoothing the spectrum level by weighting
            spectrum_levels = np.array(shared_vars.musicSpectrumLevels)
            spectrum_levels = (spectrum_levels.dot(
                0.6) + self.oldSpectrumLevels.dot(0.4)).astype(int)

            for column in range(0, LEDWall.num_columns):
                # If fallingDot is True, maximum spectrum level must be one less.
                if shared_vars.fallingDot & spectrum_levels[column] > 43:
                    spectrum_levels[column] = 43
                # Comparison of the old value of the fallingDot with the new one
                if self.fallingDotOldValue[column] <= spectrum_levels[column]:
                    self.fallingDotOldValue[column] = spectrum_levels[column]
                elif self.fallingDotOldValue[column] > 0 and self.dotFallingRate > 1:
                    self.fallingDotOldValue[column] -= 1
                # filling the pixel matrix
                for neglevel in range(0, LEDWall.num_rows - spectrum_levels[column]):
                    self.pixels[LEDWall.num_rows * column +
                                LEDWall.num_rows - 1 - neglevel] = (0, 0, 0)
                for level in range(0, spectrum_levels[column]):
                    self.pixels[LEDWall.num_rows * column +
                                level] = shared_vars.LEDPrimaryColor
                # Set fallingDot if True
                if shared_vars.fallingDot:
                    self.pixels[LEDWall.num_rows * column +
                                self.fallingDotOldValue[column]] = shared_vars.LEDSecondaryColor

                # Setting dotFallingRate to 1/3
                if self.dotFallingRate > 1:
                    self.dotFallingRate = 0
                else:
                    self.dotFallingRate += 1

            self.pixels.show()
            self.oldSpectrumLevels = spectrum_levels

    def sinus(self, iterations):
        value = [0, 0, 0, 0, 0, 0, 0, 0]
        for index in range(0, iterations):
            for c in range(0, 25):
                for i in range(0, 8):
                    value[i] = self.translate(
                        cos(i * 6.24 / 6 + c) * 100, -100, 100, 10, 34)
                    self.pixels[int(
                        value[i] + i * LEDWall.num_rows)] = (0, 0, 200)
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

    def strobo(self, shared_vars):
        while True:
            if shared_vars.kill_threads:
                break
            self.pixels.fill(shared_vars.LEDPrimaryColor)
            self.pixels.show()
            time.sleep(shared_vars.stroboFrequency *
                       shared_vars.stroboDutyCycle)
            self.pixels.fill((0, 0, 0))
            self.pixels.show()
            time.sleep(shared_vars.stroboFrequency *
                       (1 - shared_vars.stroboDutyCycle))

    def apply_brightness(self, color, brightness):
        adapted_color = np.array(color)
        adapted_color = adapted_color * brightness
        return (adapted_color.astype(int)).tolist()

    def show_color(self, color):
        self.pixels.fill(color)
        self.pixels.show()
