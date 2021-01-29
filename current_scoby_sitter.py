##### LIBRARIES #####
import time
import sys
from datetime import datetime
import os
import os.path
import glob
import inspect
import RPi.GPIO as GPIO
import atexit



### SETTINGS ###


# temp sensor settings

SLEEP_DURATION = 120 #seconds

lower_temp_limit = 22 #celcius
upper_temp_limit = 24

log_name_prefix = "bucha_log"
module_path = inspect.getfile(inspect.currentframe())
module_dir = os.path.realpath(os.path.dirname(module_path))
data_log_dir = module_dir + "/bucha_logs"

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)


os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')


# file and directory settings
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

#### FUNCTIONS ####

# temp functions
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
    lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        #temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c #, temp_f

def create_header(fn):
    if os.path.exists(fn):
        header = ""
    else:
        header = "date_time,temperature,heater_status\n"

    return header

def log_buch_temp():
    now = datetime.now()
    date_stamp = now.strftime("%Y%m%d")

    log_filename = log_name_prefix + "_" + date_stamp + ".csv"
    log_file = data_log_dir + "/" + log_filename

    log_header = create_header(log_file)

    with open(log_file, "a") as log:
        log.write(log_header)
        dt = datetime.now()
        log.write("{},{},{}\n".format(dt,bucha_temp,heater_status))
    log.close()

def cleanup():
    heater_power("off")
    
def heater_power(heater_status):

    if heater_status == "on":
        GPIO.output(11, False) #turns heater on
    elif heater_status == "off":
        GPIO.output(11, True) #turns heater off
    else:
        print("invalid heater status")
    

##### MAIN PROGRAM #####

atexit.register(cleanup)

heater_status = "off" #initialize heater status
cleanup()    
    
try:
    while True:
        bucha_temp = read_temp()
          
        print(bucha_temp)
        if bucha_temp < lower_temp_limit:
            heater_status = "on"
        elif bucha_temp > upper_temp_limit:
            heater_status = "off"
        else: 
            print("")    
        print("heater is " + heater_status)
        heater_power(heater_status)


        log_buch_temp()
        print("recording successful")
        time.sleep(SLEEP_DURATION)

except KeyboardInterrupt:
    print("keyboard interrupt")
    
#except:
#    print("an error or exception occurred")

finally:
    GPIO.cleanup()
    
    
    
