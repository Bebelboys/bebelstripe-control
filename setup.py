# die datei kann gelöscht werden, oder was ist der zweck davon? -pepe

import board
import neopixel

num_rows = 44
num_columns = 8
num_pixels_total = num_rows * num_columns
pixel_pin = board.D18
ORDER = neopixel.GRB