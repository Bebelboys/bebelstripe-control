import numpy as np


class SharedVariables:
    music_spectrum_levels = np.array(8 * [0])
    levelColor = (248, 24, 148)
    dotColor = (0, 0, 255)
    period_sec = 1.0
    duty_cycle = 0.2

    def __init__(self):
        pass
