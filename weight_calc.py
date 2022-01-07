import time
import sys
import os
import math
import datetime
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
import RPi.GPIO as GPIO
from hx711py.hx711 import HX711


PIN_DAT = 5
PIN_CLK = 6
dt_now = datetime.datetime.now()
dt_now_year = str(dt_now.year)
dt_now_month = str(dt_now.month)
dt_now_day = str(dt_now.day)

# Exit関数()
def cleanAndExit() -> None:
    print('cleaning...')
    GPIO.cleanup()
    print('Exiting program...')
    sys.exit()

# 設定関数(キャリブレーション値: int)
def setting(refUnit: int) -> any:
    hx = HX711(PIN_DAT, PIN_CLK)
    hx.set_reading_format('MSB', 'MSB')
    hx.set_reference_unit(refUnit)
    hx.reset()
    hx.tare()
    return hx

# 計測関数(HX711: any, 秒数: int)
def measurement(hx: any, sec: int) -> int:
    val = hx.get_weight(5)
    hx.power_down()
    hx.power_up()
    time.sleep(sec)
    return val

def main() -> None:
    # 初期値
    refUnit = 1
    count = 0
    id = 1
    before_weight = 0
    val_list = []

    # 必要情報入力
    cal_weight = int(input("1.Enter the calibration weight...."))
    container_weight = int(input("2.Enter the weight of the container...."))
    container_width = int(input("3.Enter the width of the container in mm...."))
    container_vertical = int(input("4.Enter the vertical of the container in mm...."))
    while True:
        file_name = input("5.Enter a name for the output file without extension....")
        file_path = "./output/"+dt_now_year+"_"+dt_now_month+"_"+dt_now_day+"/"+file_name+".csv"
        if os.path.isfile(file_path):
            print("It already exists file name.")
            continue
        else:
            break

    # キャリブレーション開始
    hx = setting(refUnit)
    while True:
        try:
            val = measurement(hx, 0.1)
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
    
    # 出力ファイル作成
    f = open(file_path, 'w')
    f.write('')
    f.close()
    df_def = pd.read_csv("./default_file/default.csv", dtype=str, encoding='SHIFT-JIS', engine='python')
    df_def.to_csv(file_path, encoding='SHIFT-JIS', index=False)

    # 計測開始
    print("-----Start measurement-----")
    hx = setting(refUnit)
    start_time = time.perf_counter()
    # df = pd.read_csv(file_path, dtype=str, encoding='SHIFT-JIS', engine='python')
    while True:
        try:
            val = measurement(hx, 1)
            print("#"+str(id)+"---------------------")
            water_weight = val - container_weight
            print("■"+str(water_weight)+"g")
            elapsed_time = Decimal(str(time.perf_counter() - start_time)).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
            precipitation = (water_weight * 1000) / (container_width * container_vertical) * (3600 / int(elapsed_time))
            print("●"+str(precipitation)+"mm/h")
            df = pd.DataFrame([[id, elapsed_time, water_weight, precipitation]])
            df.to_csv(file_path, mode='a', encoding='SHIFT-JIS', index=False, header=False)
            id += 1
        except(KeyboardInterrupt, SystemExit):
            cleanAndExit()

if __name__ == '__main__':
    main()
