import time
import sys
import os
import math
import RPi.GPIO as GPIO
from hx711py.hx711 import HX711


PIN_DAT = 5
PIN_CLK = 6



def cleanAndExit() -> None:
    print('cleaning...')
    GPIO.cleanup()
    print('Exiting program...')
    sys.exit()


def setting(refUnit: int) -> any:
    hx = HX711(PIN_DAT, PIN_CLK)
    hx.set_reading_format('MSB', 'MSB')
    hx.set_reference_unit(refUnit)
    hx.reset()
    hx.tare()
    return hx


def measurement(hx: any) -> int:
    val = hx.get_weight(5)
    
    hx.power_down()
    hx.power_up()
    time.sleep(0.1)
    return val

def main() -> None:
    refUnit = 1
    count = 0
    before_weight = 0
    val_list = []

    cal_weight = int(input("Enter the calibration weight...."))
    container_weight = int(input("Enter the weight of the container...."))

    hx = setting(refUnit)

    while True:
        try:
            val = measurement(hx)
            print(str(val)+"g")
            f, i = math.modf(val)
            if f == 0 or f == 0.0:
                print("Error value...!")
                cleanAndExit()
            print(before_weight)
            if count <= 10 and before_weight == f:
                count += 1
            elif before_weight != f:
                count = 0
            elif count > 10 and before_weight == f:
                print("Calibration now...("+str(count - 10)+"/30)")
                val_list.append(val)
                if count == 40:
                    break
                count += 1
            else:
                print("exception...")
                pass
            before_weight = f
        except(KeyboardInterrupt, SystemExit):
            cleanAndExit()
    avg = sum(val_list) / len(val_list)
    refUnit = avg // cal_weight
    print("Calibration value is "+str(refUnit)+".")
    input("Please input enter to start measurement...")
    print("-----Start measurement-----")
    hx = setting(refUnit)
    while True:
        try:
            val = measurement(hx)
            print(str(val)+"g")
        except(KeyboardInterrupt, SystemExit):
            cleanAndExit()

if __name__ == '__main__':
    main()
