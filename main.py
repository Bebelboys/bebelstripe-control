import LEDWall
import FFT
import Strobo
import SharedVariables
import threading
import sys
import time


def main():
    try:
        shared_vars = SharedVariables.SharedVariables()
        ledwall = LEDWall.LEDWall()
        fft = FFT.FFT()
        # strobo = Strobo.Strobo()

        t1 = threading.Thread(target=ledwall.music_spectrum, args=(shared_vars,))
        t1.daemon = True
        t1.start()
        # strobo_thread = threading.Thread(target=strobo.start, args=(shared_vars,))
        # strobo_thread.music_spectrum()
        t2 = threading.Thread(target=fft.start, args=(shared_vars,))
        t2.daemon = True
        t2.start()

        while True:
            time.sleep(5)

    except KeyboardInterrupt:
        print("Terminated by user ...")
        sys.exit(0)

    except Exception as e:
        print("EXCEPTION CATCHED")
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    main()