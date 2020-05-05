##### LIBRARIES #####
import time
from datetime import datetime
import os
import os.path
import glob
import inspect



### SETTINGS ###

# temp sensor settings
SLEEP_DURATION = 60 #seconds
log_name_prefix = "bucha_log"
module_path = inspect.getfile(inspect.currentframe())
module_dir = os.path.realpath(os.path.dirname(module_path))
data_log_dir = module_dir + "/bucha_logs"



os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# min/max value settings
window = []
max = 0
min = 0
maxcount = 0
mincount = 0
maxwin = 60*24 #number of measurements in 24 hours

minStatCache = 0
maxStatCache = 0
minStatNonCache = 0
maxStatNonCache = 0

# file and directory settings
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

#### FUNCTIONS ####

# min/max temp functions
def addNum(n):
    global window
    global min
    global max
    global mincount
    global maxcount

    if len(window) == maxwin:
        m = window[0]
        window = window[1:]
        if maxcount > 0 and m == max:
            maxcount = maxcount - 1
        if mincount > 0 and m == min:
            mincount = mincount - 1

    window.append(n)

    if len(window) == 1:
        max = n
        min = n
        maxcount = 1
        mincount = 1
        return

    if maxcount > 0 and n > max:
        max = n
        maxcount = 1
        return

    if mincount > 0 and n < min:
        min = n
        mincount = 1
        return

    if maxcount > 0 and n == max:
        maxcount = maxcount + 1

    if mincount > 0 and n == min:
        mincount = mincount + 1

def getMax():
    global max
    global maxcount
    global maxStatCache
    global maxStatNonCache

    if len(window) == 0:
        return None

    if maxcount > 0:
        maxStatCache = maxStatCache + 1
        return max

    max = window[0]
    maxcount = 0
    for val in window:
        if val > max:
            max = val
            maxcount = 1
        else:
            if val == max:
                maxcount = maxcount + 1
    maxStatNonCache = maxStatNonCache + 1

    return max

def getMin():
    global min
    global mincount
    global minStatCache
    global minStatNonCache

    if len(window) == 0:
        return None

    if mincount > 0:
        minStatCache = minStatCache + 1
        return min

    min = window[0]
    mincount = 0
    for val in window:
        if val < min:
            min = val
            mincount = 1
        else:
            if val == min:
                mincount = mincount + 1
    minStatNonCache = minStatNonCache + 1

    return min


#print("the min is:", newmin)
#print("the max is:", newmax)
#print("%d cached, %d non-cached"%(statCache,statNonCache))

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
        header = "date_time,temperature,min_temp,max_temp\n"

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
        log.write("{},{},{},{}\n".format(dt,bucha_temp,min,max))
    log.close()

##### MAIN PROGRAM #####
while True:
    bucha_temp = read_temp()
    addNum(bucha_temp)
    getMin()
    getMax()
    log_buch_temp()
    print("recording successful")
    time.sleep(SLEEP_DURATION)
