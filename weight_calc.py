import time
import sys
import os
import math
import RPi.GPIO as GPIO
from hx711py.hx711 import HX711

PIN_DAT = 5
PIN_CLK = 6



def cleanAndExit():
    print('cleaning...')
    GPIO.cleanup()
    print('complete')
    sys.exit()


def setting(refUnit):
    hx = HX711(PIN_DAT, PIN_CLK)
    hx.set_reading_format('MSB', 'MSB')
    hx.set_reference_unit(refUnit)
    hx.reset()
    hx.tare()
    return hx


def measurement(hx):
    val = hx.get_weight(5)
    print(val)
    hx.power_down()
    hx.power_up()
    time.sleep(0.1)
    return val

def main():
    refUnit = 1
    count = 0
    before_weight = 0
    val_list = []

    def_weight = int(input("重量を入力してください..."))

    hx = setting(refUnit)

    while True:
        try:
            val = measurement(hx)
            f, i = math.modf(val)
            print(f)
            print(before_weight)
            print(count)
            if count < 10 and before_weight == f:
                count += 1
            elif before_weight != f:
                count = 0
            elif count == 10 and before_weight == f:
                val_list.append(val)
                if len(val_list) == 30:
                    break
            else:
                print("例外です。")
                pass
            before_weight = f
        except(KeyboardInterrupt, SystemExit):
            # panel.display_clear()
            cleanAndExit()
    avg = sum(val_list) / len(val_list)
    refUnit = avg // def_weight
    print("キャリブレーション値は、"+str(refUnit)+"です。")
    input()
    print("-----本計測開始-----")
    # hxをリセットする処理を追加？
    hx = setting(refUnit)

    print('Tare done! Add weight now...')

    while True:
        try:
            val = measurement(hx)
        except(KeyboardInterrupt, SystemExit):
            # panel.display_clear()
            cleanAndExit()

if __name__ == '__main__':
    main()
