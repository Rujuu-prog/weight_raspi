import time
import sys
import RPi.GPIO as GPIO
from hx711py.hx711 import HX711

PIN_DAT = 5
PIN_CLK = 6

refUnit = 1

def cleanAndExit():
    print('cleaning...')
    GPIO.cleanup()
    print('complete')
    sys.exit()

def main():
    hx = HX711(PIN_DAT, PIN_CLK)
    hx.set_reading_format('MSB', 'MSB')
    hx.set_reference_unit(refUnit)
    hx.reset()
    hx.tare()

    print('Tare done! Add weight now...')

    while True:
        try:
            val = hx.get_weight(5)
            print(val)

            hx.power_down()
            hx.power_up()
            time.sleep(0.1)

        except(KeyboardInterrupt, SystemExit):
            panel.display_clear()
            cleanAndExit()

if __name__ == '__main__':
    main()