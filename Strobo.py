import numpy as np
import time

class Strobo:
    def __init__(self):
        self.strobo_period_sec = 0.1
        self.light_impulse_duty_cycle = 0.2
        self.max_spectrum_level = 44
        self.led_columns = 8

    def start(self, var):
        while True:
            var.spec_levels = np.array(self.led_columns * [self.max_spectrum_level])
            time.sleep(self.strobo_period_sec * self.light_impulse_duty_cycle)
            var.spec_levels = np.array(self.led_columns * [0])
            time.sleep(self.strobo_period_sec * (1 - self.light_impulse_duty_cycle))