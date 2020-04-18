import LEDWall
import FFT
from strobo import Strobo
import SharedVariables
import threading
import time


def main():
    try:
        var = SharedVariables.SharedVariables()
        ledwall = LEDWall.LEDWall()
        fft = FFT.FFT()
        #strobo = Strobo()

        t1 = threading.Thread(target=ledwall.start, args=(var,))
        t1.start()
        # strobo_thread = threading.Thread(target=strobo.start, args=(var,))
        # strobo_thread.start()
        t2 = threading.Thread(target=fft.start, args=(var,))
        t2.start()

    except Exception as e:
        print("EXCEPTION CATCHED")
        print(e)


if __name__ == '__main__':
    main()