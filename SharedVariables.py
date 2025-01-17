import numpy as np


class SharedVariables:
    on = True
    mode = 'music'
    kill_threads = False
    brightness = 1.0
    LEDBrightness = 1.0
    primaryColor = [248, 24, 148]
    LEDPrimaryColor = [248, 24, 148]
    secondaryColor = [0, 0, 255]
    LEDSecondaryColor = [0, 0, 255]
    musicSpectrumLevels = np.array(8 * [0])
    fallingDot = True
    fftWeightings = [4, 4, 8, 16, 32, 32, 64, 128]
    stroboFrequency = 0.05
    stroboDutyCycle = 0.5
    ambientPulsing = True
    ambientFrequency = 10.0

    def __init__(self):
        pass

    def list_settings(self):
        settings = {
            'general': {
                'brightness': self.brightness
            },

            'color': {
                'primaryColor': self.primaryColor,
                'secondaryColor': self.secondaryColor
            },

            'music': {
                'fallingDot': self.fallingDot,
                'fftWeightings': self.fftWeightings
            },

            'strobo': {
                'frequency': self.stroboFrequency,
                'dutyCycle': self.stroboDutyCycle
            },

            'ambient': {
                'pulsing': self.ambientPulsing,
                'frequency': self.ambientFrequency
            }
        }
        return settings

    def list_control(self):
        control = {
            'on': self.on,
            'mode': self.mode
        }
        return control
