import numpy as np


class SharedVariables:
    on = True
    mode = enumerate('music', 'strobo', 'ambient')
    brightness = 1.0
    primaryColor = [248, 24, 148]
    secondaryColor = [0, 0, 255]
    musicSpectrumLevels = np.array(8 * [0])
    fallingDot = True
    dotSpeed = 1
    fftWeightings = [4, 4, 8, 16, 32, 32, 64, 128]
    stroboFrequency = 0.05
    stroboDutyCycle = 0.5
    ambientPulsing = True
    ambientFrequency = 10.0

    def __init__(self):
        pass
