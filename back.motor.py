#!/usr/bin/env python

# Import required modules
import time
try:
        import RPi.GPIO as GPIO
except RuntimeError:
        print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

print(GPIO.RPI_INFO)

# Declare the GPIO settings
GPIO.setmode(GPIO.BOARD)

# set up GPIO pins
GPIO.setup(7, GPIO.OUT) # Connected to PWMA
GPIO.setup(11, GPIO.OUT) # Connected to AIN2
GPIO.setup(12, GPIO.OUT) # Connected to AIN1
GPIO.setup(13, GPIO.OUT) # Connected to STBY
GPIO.setup(15, GPIO.OUT) # Connected to BIN1
GPIO.setup(16, GPIO.OUT) # Connected to BIN2
GPIO.setup(18, GPIO.OUT) # Connected to PWMB
time.sleep(1)

# Drive the motor clockwise
print("driving motor a,b")
# Motor A:
GPIO.output(12, GPIO.HIGH) # Set AIN1
GPIO.output(11, GPIO.LOW) # Set AIN2
# Motor B:
GPIO.output(15, GPIO.HIGH) # Set BIN1
GPIO.output(16, GPIO.LOW) # Set BIN2

# Set the motor speed
# Motor A:
pa = GPIO.PWM(7, 4000) # Set PWMB
# Motor B:
pb = GPIO.PWM(18, 4000) # Set PWMB
pa.start(100)
pb.start(100)

# Disable STBY (standby)
GPIO.output(13, GPIO.HIGH)

# Wait 5 seconds
remaining = 5
while remaining > 0:
    print("sleep " + str(remaining))
    time.sleep(1)
    remaining-=1

# Reset all the GPIO pins by setting them to LOW
GPIO.output(12, GPIO.LOW) # Set AIN1
GPIO.output(11, GPIO.LOW) # Set AIN2
GPIO.output(7, GPIO.LOW) # Set PWMA
GPIO.output(13, GPIO.LOW) # Set STBY
GPIO.output(15, GPIO.LOW) # Set BIN1
GPIO.output(16, GPIO.LOW) # Set BIN2
GPIO.output(18, GPIO.LOW) # Set PWMB


GPIO.cleanup()
