####################################################################################################################################
#Written by: Jonathan Moore (jonathanm@vt.edu) and Mathew Florence
#Property of Virginia Tech under the supervision of Dr. Nina Stark
#Purpose: This code takes in measurements from two bar100 blue robotics pressure sensors and a real time clock. The pressure and time
        # measurements are stored to a sd card.
# This code is written in circuit python. The Mu ide should be used to edit/debug this code
    # Mu ide download link (https://codewith.mu/en/download)

# Helpful resources

    # Circuit Python Tips and Tricks
        #https://github.com/todbot/circuitpython-tricks#make-and-use-a-config-file

    # Hardware components
        # 2- Bar100 pressure sensors (https://bluerobotics.com/store/sensors-sonars-cameras/sensors/bar100-sensor-r2-rp/)
        # 1- TCA9548A i2c multiplexer (https://www.adafruit.com/product/2717)
        # 1- Metro M4 Express (https://learn.adafruit.com/adafruit-metro-m4-express-featuring-atsamd51)
        # 1- Arduino data logging shield with built in Real Time Clock (rtc) (https://learn.adafruit.com/adafruit-data-logger-shield)
        # 1- Micro-sd to Sd convertor (SanDisk-microSD-Memory-Adapter-MICROSD-ADAPTER)
        # 1- 2" x 3" perf board (https://www.circuitspecialists.com/64-8933.html)
        # 28 AWG wire (StrivedayTM-Flexible-Silicone-electronic-electrics)
        # 3- JST-PH 2.0mm male/female connectors (https://www.amazon.com/Pieces-JST-PHR-Connector-Female-Header/dp/B0731MZCGF)

    # Software/Debugging/manual resources
        # Learn how to use the TCA9548A i2c multiplexer - https://learn.adafruit.com/adafruit-tca9548a-1-to-8-i2c-multiplexer-breakout/overview
        # Learn i2c and SPI - https://learn.adafruit.com/circuitpython-basics-i2c-and-spi/i2c-devices
        # Communicate with rtc - https://docs.circuitpython.org/en/latest/shared-bindings/rtc/index.html
        # KellerLD sensor manual (http://www.keller-druck2.ch/swupdate/InstallerD-LineAddressManager/manual/Communication_Protocol_4LD-9LD_en.pdf)
        # KellerLD python code (https://github.com/bluerobotics/KellerLD-python)
            # NOTE: The above code is in python. This device runs on circuit python, therefore the linked code cannot be just copied and pasted
                    # The code on this device and in the back up file on google drive has been converted to circuit python. The converted code
                    # is very similar to the original python code.
# Notes
    # Pressure readings are abosolute pressure (they are reading the pressure of the atmosphere) and made in bar
    # Temperature readings are in celcius
    # Printing tuples in Mu plots the data to Mu's built in data plotter
####################################################################################################################################





#""" uncomment to comment entire code
import board
import busio
import mount_sd #Imports file to initialize sd card
import array
import digitalio
import neopixel
import adafruit_pcf8523
import adafruit_tca9548a
from kellerLD import KellerLD
import time
import sys

# Legend of connected i2c devices with hexadecimal id
    # TCA (Multiplexer) - 0x70
    # real time clock (rtc) - 0x68
    # Blue robotics bar 100 pressure & temp sensor - 0x40

# Create I2C bus
print("i2c check-up begins..")
i2c = board.I2C()  # uses board.SCL and board.SDA

# Create the TCA9548A object and give it the I2C bus
tca = adafruit_tca9548a.TCA9548A(i2c)

for channel in range(8):
    if tca[channel].try_lock(): # try locking each channel of the tca
        print("Channel {}:".format(channel), end="") #print the current channel
        addresses = tca[channel].scan() # scan the addresses on each channel
        print([hex(address) for address in addresses if address !=0x70]) # prints the i2c devices connected
        tca[channel].unlock() # Unlock the channel so that it open for the sensor
print("i2c initialization done")

led = neopixel.NeoPixel(board.NEOPIXEL, 1) # create the led pixel class
led.brightness = 0.02 # set the led brightness
rtc = adafruit_pcf8523.PCF8523(tca[1]) # set the rtc onto the first channel of the tca

if False:
    t = time.struct_time((2022, 7, 5, 11, 22, 45, 0, -1, -1)) # Create the time structure
    rtc.datetime = t # set the rtc to the time structure created above




size = 50 # Number of element entries before saving to sd card (array size)
#Create the arrays to store readings from the rtc and pressure sensors

    #array.array("d", [0]*size)
        # Creates a zero array with decimal format and size length
    #array.array("I", [0]*size)
        # Creates a zero array with integer format and size length
pres1 = array.array("d", [0]*size)
pres2 = array.array("d", [0]*size)
#temp1 = array.array("d", [0]*size) # Array to store sensor 1 temp readings
#temp2 = array.array("d", [0]*size) # Array to store sensor 2 temp readings
clock = array.array("d", [0]*size)
Iarray = array.array("I", [0]*size)
month = array.array("I", [0]*size)
day = array.array("I", [0]*size)
hour = array.array("I", [0]*size)
minutes = array.array("I", [0]*size)
second = array.array("I", [0]*size)
dt_1 = array.array("I",[0]*size)
dt_2 = array.array("I", [0]*size)

############ Pressure sensor Init and reading ##################

# Selects the channel of the tca that the pressure sensor is on, the
sensor1 = KellerLD(1, tca[0]) # Selects channel 0 for sensor 1
sensor2 = KellerLD(2, tca[4]) # Selects channel 4 for sensor 2

sensor1.init() # Initialize pressure sensor 1
sensor2.init() # Initialize pressure sensor 2

if not sensor1.init() and sensor2.init(): # Check if the sensor is properly initiated
    if not sensor1.init():
        print("Failed to initialize Keller LD sensor 1!")
    exit(1)
    if not sensor2.init():
        print("Failed to initialize Keller LD sensor 2!")
    exit(1)

#########Main Loop#################

i = 0
fileName = "p1p2time_FlumeTest_v2.txt".format(size)
print("Writing to " + fileName)
with open("/sd/" + fileName, "a") as f: # We open a file called p1p2time.txt
    led[0] = (70, 0, 130) # Set the led on the mcu to purple to indicate we are running the code
    while True: # set to "while True" when debugging is finished

        t = rtc.datetime # query the real time clock, year, month, day, weekday, hours, minutes, seconds, subseconds
        #print(t) #uncomment for debugging
        #time.sleep(0.003)
        nano_init = time.monotonic_ns()#  The nano seconds at the call to the real time clock (rtc)
        #print(nano_init) # Uncomment for debugging

        for x in range(0, size, 1): # For loop for a variable, x, that goes from 0 : 1 : 16
            Iarray[x] = i # This is a counter for the storage of the elements move this out of the loop
            month[x] = t.tm_mon # Stores the month
            day[x] = t.tm_mday # Stores the day
            hour[x] = t.tm_hour # Store the hour
            minutes[x] = t.tm_min # Store the minute
            second[x] = t.tm_sec # Store the second

            try:
                time.sleep(0.01)
                dt_1[x] = time.monotonic_ns() - nano_init # Nano second difference from the point of initial reading for first sensor
                sensor1.read() # Read the first sensor
                time.sleep(0.003) # Wait so the i2c line doesn't get clogged

                dt_2[x] = time.monotonic_ns() - nano_init # Nano second difference from the point of initial reading for second sensor
                sensor2.read() # Read the first sensor
                time.sleep(0.003) # Wait so the i2c line doesn't get clogged

                #print((sensor1.pressure(),sensor2.pressure())) # Uncomment to plot data to Mu plotter
                #print("Sensor: {} \nPressure: {} bar \nTemperature: {} C".format(sensor1.sensorID, sensor1.pressure(), sensor1.temperature())) # Uncomment for debugging
                #print("Sensor: {} \nPressure: {} bar \nTemperature: {} C".format(sensor2.sensorID, sensor2.pressure(), sensor2.temperature()))  # Uncomment for debugging

                pres1[x] = sensor1.pressure() # Store sensor 1 pressure reading
                pres2[x] = sensor2.pressure() # Store sensor 2 pressure reading

            except Exception as e:
                print(e) # Print exceptions that come up while reading the sensors
            i = i + 1
            if i % 100 == 0: # Prints 1 every 100 sensor reads
                print("{} sensor reads".format(i))

        for x in range(0, size, 1): # Index up to size counting by one
            # Write the date, pressure reading, and index of each reading to the sd card
            dataLine = ('{} {} {} {} {} {} {} {} {}\n'.format(month[x], day[x], hour[x], minutes[x], second[x], dt_1[x], pres1[x], pres2[x], Iarray[x])) # add dt_2 to this file save 07/21/22
            f.write(dataLine)

            #f.write('{} {} {} {} {} {} {} {} {}\n'.format(month[x], day[x], hour[x], minutes[x], second[x], nano_1[x], pres1[x], pres2[x], Iarray[x]))
            #f.write commad when testing with only one sensor
            #f.write('{} {} {} {} {} {} {} {}\n'.format(month[x], day[x], hour[x], minutes[x], second[x], nano_1[x], pres1[x], Iarray[x]))
        f.flush() # Cleans the sd card buffer

print("Sensor reading is complete! :)") # Uncomment for debugging"""
