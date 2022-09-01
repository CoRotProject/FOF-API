from palette import palette
from festofactory import FestoFactory
import time


if __name__ == "__main__":

    PALETTE_LIST = []
    NUMBER_OF_PALETTE = 14

    for index in range(NUMBER_OF_PALETTE):
        PALETTE_LIST.append(palette(index+1))
        PALETTE_LIST[index].start()
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        for index in range(NUMBER_OF_PALETTE):
            PALETTE_LIST[index].terminate()
    print("killed")