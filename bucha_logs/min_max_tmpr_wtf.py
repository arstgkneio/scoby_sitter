import datetime
import os
import glob
import inspect

# Timedelta object for a sample window of the desired length expressed in hours
window_hrs = 24
inclusion_period_length = datetime.timedelta(hours=window_hrs)
file_prefix = 'bucha_log'

# Gets the canonical path, eliminating any symbolic links
module_path = inspect.getfile(inspect.currentframe())

# Builds working directory using canonical path
module_dir = os.path.realpath(os.path.dirname(module_path))
path = module_dir + "/bucha_logs"

# Datetime object for the current date and time
current_datetime = datetime.datetime.now()

# Datetime format that will be used to format datetime strings read from the data files.
# Change it to match your data
datetime_format = '%Y-%m-%d %H:%M:%S.%f'

# Create a file handle for the file that will contain the sample data
#window_data_filename = 'window_data.csv'
#window_data_out_fh = open(window_data_filename, 'w')

# Opbtain the list of the filenames for the files that contain the
# temperature data according to the length of the window
#tmpr_data_file_name_prefix = 'bucha_log_'
# number_of_files = int(window_hrs/24)+1
#
# print("The number of data files is:", number_of_files)
#
# file_list = sorted(glob.glob(path + '/' + file_prefix + '*.csv'))
# print(file_list)
# #file_list.sort()
# file_list = file_list[-number_of_files:]
#
# print(file_list)
file_list_test = path + "/" + file_prefix
print(file_list_test)
file_list = glob.glob(path + '/' + file_prefix + '*.csv')
#print(file_list)
file_list.sort()
#print(file_list)
datafile = file_list[-1] #most recent data file
#print(file_list)

with open(datafile, 'rb') as f:
    f.seek(-2, os.SEEK_END)
    while f.read(1) != b'\n':
        f.seek(-2, os.SEEK_CUR)
    last_line = (f.readline().decode())
    print(last_line)

# Itterate through the list of the data files to
# identify records that fall within the sample window
# and output these into the window data file
stop = False
cnt=0
for file in reversed(file_list):
#for file in file_list:

    print(file)
    # For each input file create a file handle...
    data_filehandle = open(file, 'r')

    # ...and read it in the reversed order one record at a time
    for rec in reversed(list(data_filehandle)):
        cnt+=1

        # Strip the newline char
        rec = rec.strip()

        # Capture the value from the first field...
        datetimestamp = rec.split(',')[0]
        # ...and store it in a datetime object using the format defined earlier
        rec_datetime = datetime.datetime.strptime(datetimestamp, datetime_format)

        # Calculate the age of the record
        rec_age = current_datetime - rec_datetime

        # If the record's age is less or equal to the size of the sample window
        # store the record. In this case in the window date file
        if(rec_age <= inclusion_period_length):
            window_data_out_fh.write(rec + "\n")
        else:
            stop = True
            break

    data_filehandle.close()

    if(stop):
        break

window_data_out_fh.close()
print(cnt)

# Find min and max temperature values in sample records
window_data_in_fh = open(window_data_filename, "r")

tmpr_list = []

for tmpr_rec in window_data_in_fh:
    tmpr_rec = tmpr_rec.strip()
    tmpr_value = tmpr_rec.split(',')[1]

    tmpr_list.append(tmpr_value)

window_data_in_fh.close()

if(len(tmpr_list)):
    print(min(tmpr_list))
    print(max(tmpr_list))
else:
    print('none')
