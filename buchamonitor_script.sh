# This bash script script runs both the temperature recording program and the display program simultaneously

# Assigns environment variable necessary for display program 
export DISPLAY=:0.0 

python3 /home/pi/BuchaMonitor/temp_output.py &

python3 /home/pi/BuchaMonitor/RaspBucha_Display.py &


# to run on boot with crontab add "@reboot sleep 30 && <PATH_GOES_HERE>/buchamonitor_script.sh 2><PATH_GOES_HERE>/error_log.txt &"
# see "running_python_programs_on_start_up.txt" for more information
