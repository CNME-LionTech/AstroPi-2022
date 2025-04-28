# Description:  Program written by Team LionTech from
#               Colegiul National "Mihai Eminescu" Oradea, Romania for
#               Phase 2 of AstroPi Mission Space Lab competition 2021/2022
# Team Members: Elisa Erzse, Vlad Marian, Mihnea Popovici,
#               Mădălin Toma, Andrei Droj
# Teacher:      Amelia Stoian


# Libraries needed for experiment
from sense_hat import SenseHat
import datetime as dt
from time import sleep
from picamera import PiCamera
from orbit import ISS
from skyfield.api import load
import os, csv, sys

# SenseHat Initialisation
sense = SenseHat()
sense.clear()

# Starting the camera
cam = PiCamera()
cam.resolution = (2592, 1944)

# Mission parameters
missiontime = 175       # Running time in minutes
team = 'LionTech'       # AstroPi team name
photo_counter = 1
photo_delay = 10

# Working path definition
dir_path = os.path.dirname(os.path.realpath(__file__))

# Datetime variables to store the start time and the current time
start_time = dt.datetime.now()
now_time = dt.datetime.now()
last_photo_time = dt.datetime.now()
file_time_stamp = start_time.strftime('%Y%b%d_%Hh%Mm%Ss')
timescale = load.timescale()

# Load ephemeris data
ephemeris = load('de421.bsp')

# Create folders for images and logs
ltdata = dir_path + '/LTdata'
if (not os.path.exists(ltdata)):
    os.mkdir(ltdata)
if (not os.path.exists(ltdata + '/logs/')):
    os.mkdir(ltdata + '/logs/')
if (not os.path.exists(ltdata + '/images/')):
    os.mkdir(ltdata + '/images/')
if (not os.path.exists(ltdata + '/images/{}'.format(file_time_stamp))):
    os.mkdir(ltdata + '/images/{}'.format(file_time_stamp))
logfilename = ltdata + '/logs/LionTech_Log_{}.csv'.format(file_time_stamp)
errorfilename = ltdata + '/logs/Errors{}.txt'.format(file_time_stamp)

# Latest TLE data for ISS location
location = ISS.coordinates()


def readAccelerations():
    """ Function for reading the accelerations on the three axes.
    The reading contains the acceleration on x, y and z-axis, in
    variables rawAccelX, rawAccelY and rawAccelZ.
    """

    sense.set_imu_config(False, False, True)
    rawAccel = sense.get_accelerometer_raw()
    rawAccelX = round(rawAccel['x'],3)
    rawAccelY = round(rawAccel['y'],3)
    rawAccelZ = round(rawAccel['z'],3)
    return rawAccelX, rawAccelY, rawAccelZ


def readCompass():
    """ Function for reading the data from the compass. The readings
    contains both the direction of the North, in variable comp, and
    the magnetic intensity on x, y and z-axis, in variables rawCompX,
    rawCompY and rawCompZ.
    """

    sense.set_imu_config(True, False, False)
    comp = round(sense.get_compass(),3)
    rawComp = sense.get_compass_raw()
    rawCompX = round(rawComp['x'],3)
    rawCompY = round(rawComp['y'],3)
    rawCompZ = round(rawComp['z'],3)

    return comp, rawCompX, rawCompY, rawCompZ


def readOrientation():
    """ Function for reading the SenseHat orientation data. The readings 
    contain the pitch, roll and yaw as separate values.
    """

    sense.set_imu_config(False, True, True)
    rawAccel = sense.get_orientation()
    pitch = round(rawAccel['pitch'],2)
    roll = round(rawAccel['roll'],2)
    yaw = round(rawAccel['yaw'],2)
    return pitch, roll, yaw


def convert(angle):
    """ Convert an ephem angle (degrees:minutes:seconds) to an
    EXIF-appropriate representation (rationals). Return a tuple
    containing a boolean and the converted angle, with the
    boolean indicating if the angle is negative.
    """
    sign, degrees, minutes, seconds = angle.signed_dms()
    exif_angle = '{:.0f}/1,{:.0f}/1,{:.0f}/10'.format(abs(degrees), minutes, seconds*10)

    return degrees < 0, exif_angle


def create_csv(data_file):
    """ Creates the CSV file and the header of the log file.
    """
    
    with open(data_file, 'w', buffering=1) as f:
        writer = csv.writer(f)
        header = ('Team','Timestamp','Longitude','Latitude','Height','Temperature','Temp_from_pressure','Humidity','Pressure','AccelX','AccelY','AccelZ','CompassMag','CompassX','CompassY','CompassZ','Pitch','Roll','Yaw')
        writer.writerow(header)


def add_csv_data(data_file, data):
    """ Function to add data to the CSV log file.
    """
    
    with open(data_file, 'a', buffering = 1) as f:
        writer = csv.writer(f)
        writer.writerow(data)
    

# Print iterations progress
def printProgress (iteration, total, prefix = '', suffix = '', decimals = 1):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
    """
    percent = ('{:' + str(decimals+4) + '.' + str(decimals) + 'f}').format(100 * (iteration / float(total)))
    print('{} {}% {}'.format(prefix, percent, suffix), flush=True)
    sys.stdout.flush()

    # Print New Line on Complete
    if iteration == total: 
        print()


# main programm
print('LionTech Mission Space Lab')
print('- Systems checked at:         {}'.format(now_time.strftime('%Y-%b-%d %Hh%Mm%Ss')))
print('- Data collection started at: {}'.format(now_time.strftime('%Y-%b-%d %Hh%Mm%Ss')))
print('- Collecting data .................................')

try: 
    create_csv(logfilename)
except Exception as e:
    with open(errorfilename, 'a') as f:
        f.write('Mission error: ' + str(e) + '\n')

current_iteration = 0
while (now_time < start_time + dt.timedelta(minutes = missiontime)):

    try:
        # Update the current time
        sleep(0.25)
        now_time = dt.datetime.now()

        # Compute ISS location
        location = ISS.coordinates()
        latitude = round(location.latitude.degrees, 6)
        longitude = round(location.longitude.degrees, 6)
        height = round(location.elevation.km, 2)

        # Convert the latitude and longitude to EXIF-appropriate representations
        south, exif_latitude = convert(location.latitude)
        west, exif_longitude = convert(location.longitude)        

        # Read the temperature, humidity, pressure and other data from the SenseHat
        temperature = round(sense.get_temperature(), 3)
        temp_p = round(sense.get_temperature_from_pressure(), 3)
        humidity = round(sense.get_humidity(), 3)
        pressure = round(sense.get_pressure(), 3)
        accelX, accelY, accelZ = readAccelerations()
        compassMag, compassX, compassY, compassZ = readCompass()
        pitch, roll, yaw = readOrientation()

        # Zip readings in a single variable and write them to the csv
        rowdata = (team, now_time,longitude,latitude,height,temperature,temp_p,humidity,pressure,accelX,accelY,accelZ,compassMag,compassX,compassY,compassZ,pitch,roll,yaw)
        add_csv_data(logfilename, rowdata)
        # print(rowdata)

        # Convert the latitude and longitude to EXIF-appropriate representations
        south, exif_latitude = convert(location.latitude)
        west, exif_longitude = convert(location.longitude)

        # Set the EXIF tags specifying the current location
        cam.exif_tags['GPS.GPSLatitude'] = exif_latitude
        cam.exif_tags['GPS.GPSLatitudeRef'] = "S" if south else "N"
        cam.exif_tags['GPS.GPSLongitude'] = exif_longitude
        cam.exif_tags['GPS.GPSLongitudeRef'] = "W" if west else "E"

        # Image capture
        if now_time > last_photo_time + dt.timedelta(seconds = photo_delay):
            t = timescale.now()
            if ISS.at(t).is_sunlit(ephemeris):
                cam.capture(ltdata + '/images/{}/LTech_{:04d}.jpg'.format(file_time_stamp, photo_counter))
                photo_counter += 1
                last_photo_time = now_time
                with open(errorfilename, 'a') as f:
                    f.write('Mission update: {} ISS in light\n'.format(now_time))
            else:
                with open(errorfilename, 'a') as f:
                    f.write('Mission update: {} ISS in shadow\n'.format(now_time))
        last_iteration = current_iteration
        current_iteration = (now_time - start_time).seconds // 600 # mesuring time progress by 10 minutes 
        if current_iteration != last_iteration:
            printProgress(current_iteration * 10, missiontime, prefix = '-   Progress:', suffix = 'Complete')

    except Exception as e:
        with open(errorfilename, 'a') as f:
            f.write('Mission error: ' + str(e) + '\n')

print('- Mission ended at:           {}'.format(now_time.strftime('%Y-%b-%d %Hh%Mm%Ss')))
print('- Total runtime:              {}'.format((now_time - start_time)))
print('Mission accomplished - Team LionTech')
sense.clear()