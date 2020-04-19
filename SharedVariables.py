import numpy as np


class SharedVariables:
    brightness = 1.0
    musicSpectrumLevels = np.array(8 * [0])
    primaryColor = [248, 24, 148]
    dot = True
    secondaryColor = [0, 0, 255]
    stroboFrequency = 0.05
    stroboDutyCycle = 0.5

    def __init__(self):
        pass
