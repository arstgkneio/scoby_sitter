import datetime
import os
import glob
import inspect

#===============================================================================
#TODO: get all times which correspond to min/max values, if there is more than 1
#===============================================================================
#===============================================================================
#TODO: calculate relative time in hours/minutes if relative_time = True
#===============================================================================

def get_extrema(last_n_hours):
    file_prefix = 'bucha_log'
    module_path = inspect.getfile(inspect.currentframe())
    module_dir = os.path.realpath(os.path.dirname(module_path))
    path = module_dir + "/bucha_logs"

    #self.last_n_hours = 24 # number of hours over which min/max are to be calculated
    hour_range = datetime.timedelta(hours=last_n_hours)
    temp_min = 0
    temp_max = 0
    hour_range_data = {}

    # number of included data files should depend on hour_range
    number_of_files = int(last_n_hours/24) + 1
    file_list = glob.glob(path + '/' + file_prefix + '*.csv')
    file_list.sort()
    file_list = file_list[-number_of_files:]

    # included entries are greater than current time by at most the hour_range
    stop = False
    for file in reversed(file_list):
        #print(file)
        # For each input file create a file handle...
        data_filehandle = open(file, 'r')

        # ...and read it in the reversed order one record at a time
        for rec in reversed(list(data_filehandle)):

            # Strip the newline char
            rec = rec.strip()

            # Capture the value from the first field...
            datetimestamp = rec.split(',')[0]

            # ...and store it in a datetime object using the format defined earlier
            #rec_datetime = datetime.datetime.strptime(datetimestamp, "%Y-%m-%d %H:%M:%S.%f")
            #come up with a more delicate way of excluding header row
            try:
                rec_datetime = datetime.datetime.strptime(datetimestamp, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                continue
            # Calculate the age of the record
            current_datetime = datetime.datetime.now()
            rec_age = current_datetime - rec_datetime
            # If the record's age is less or equal to the size of the sample window
            # store the record in a dictionary
            if(rec_age <= hour_range):
                rec_temperature = float(rec.split(',')[1])
                hour_range_data[datetimestamp] = rec_temperature
            else:
                stop = True
                break

        data_filehandle.close()

        if(stop):
            break

    # Finding min/max values in dictionary and corresponding key
    dt_min_temperat = min(hour_range_data, key=hour_range_data.get)
    #print(dt_min_temperat)
    min_temperat = hour_range_data.get(dt_min_temperat)
    #print(type(min_temperat))

    dt_max_temperat = max(hour_range_data, key=hour_range_data.get)
    max_temperat = hour_range_data.get(dt_max_temperat)

    # Convert datetimes to day, month, hour, minute format
    dt_min_temperat = datetime.datetime.strptime(dt_min_temperat, "%Y-%m-%d %H:%M:%S.%f")
    dt_min_temperat = datetime.datetime.strftime(dt_min_temperat, "%d %b %H:%M")


    dt_max_temperat = datetime.datetime.strptime(dt_max_temperat, "%Y-%m-%d %H:%M:%S.%f")
    dt_max_temperat = datetime.datetime.strftime(dt_max_temperat, "%d %b %H:%M")

    return(float(min_temperat), dt_min_temperat, float(max_temperat), dt_max_temperat)

#
# min_temperat, dt_min_temperat, max_temperat, dt_max_temperat = get_extrema()
#
# print("The high value of temperature was:", max_temperat, "which happened at:", dt_max_temperat)
# print("The low value of temperature was:", min_temperat, "which happened at:", dt_min_temperat)
