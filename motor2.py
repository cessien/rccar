#!/usr/bin/env python3

# Import required modules
import threading
from queue import Queue
import time
import math
import signal
import socket
import struct
import sys
import argparse
import json
from evdev import InputDevice, categorize, ecodes

try:
        import RPi.GPIO as GPIO
except RuntimeError:
        print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

parser = argparse.ArgumentParser(description='rc car motor controller')
parser.add_argument('--debug', dest='debug', action='store_true', help='max motors on a timer')

args = parser.parse_args()

gamepad = InputDevice('/dev/input/event0')

rTgr = 311 

def setup_multicast():
    multicast_group = '230.0.0.0'
    server_address = ('', 4446)
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(server_address)
    group = socket.inet_aton(multicast_group)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

def drive(s = 49):
    if s > 43 and s < 55:
        s = 0
    elif s <= 43:
        # Reverse
        GPIO.output(12, GPIO.HIGH) # Set AIN1
        GPIO.output(11, GPIO.LOW) # Set AIN2
        s = math.floor(100 - s/43 * 100)
    else:
        # Forward
        GPIO.output(12, GPIO.LOW) # Set AIN1
        GPIO.output(11, GPIO.HIGH) # Set AIN2
        s = math.floor((s - 55)/55 * 100 )

    s =  100 if s > 100 else  s
    s =  0   if s < 0   else s

    # Set the motor speed
    pa.ChangeDutyCycle(s)
    pb.ChangeDutyCycle(s)
    # Disable STBY (standby)
    GPIO.output(16, GPIO.HIGH)

def turn(a = 90):
    a = alignment(a)
    t = 6 + 3 * a / 180
    #a = 7.5 if a >=7 and a <=8 else a 

    t = round(t,1)
    # Set the turn angle
    servo.ChangeDutyCycle(t)

def alignment(a):
    a = a + 50
    a = 0 if a < 0 else a
    a = 180 if a > 180 else a
    return a

def setup():
    print(GPIO.RPI_INFO)
    # Declare the GPIO settings
    GPIO.setmode(GPIO.BOARD)
    ##### set up GPIO pins chip 1
    GPIO.setup(37, GPIO.OUT) # Connected to PWMA, GPIO 26
    GPIO.setup(11, GPIO.OUT) # Connected to AIN2, GPIO 17 
    GPIO.setup(12, GPIO.OUT) # Connected to AIN1, GPIO 18
    GPIO.setup(16, GPIO.OUT) # Connected to STBY, GPIO 23
    GPIO.setup(15, GPIO.OUT) # Connected to BIN1, GPIO 22
    GPIO.setup(22, GPIO.OUT) # Connected to BIN2, GPIO 25
    GPIO.setup(18, GPIO.OUT) # Connected to PWMB, GPIO 24
    GPIO.setup(33, GPIO.OUT) # Connected to SERVO, GPIO 13
    time.sleep(1)
    # Motor A:
    GPIO.output(12, GPIO.LOW) # Set AIN1
    GPIO.output(11, GPIO.HIGH) # Set AIN2
    # Motor B:
    GPIO.output(15, GPIO.HIGH) # Set BIN1
    GPIO.output(22, GPIO.LOW) # Set BIN2
    global pa
    global pb
    # Motor A (chip 1):
    pa = GPIO.PWM(37, 100) # Set PWMA
    # Motor B (chip 1):
    pb = GPIO.PWM(18, 100) # Set PWMB
    pa.start(0)
    pb.start(0)

    global servo
    servo = GPIO.PWM(33, 50)
    servo.start(7.5)

def cleanup():
    print("cleaning up")
    GPIO.cleanup()

def signal_handler(sig, frame):
    print('Caught Ctrl+C! Exiting cleanly')
    cleanup()
    sys.exit(0)

def receive_multicast():
    global speed
    global angle
    while True:
        #data, address = sock.recvfrom(1024)
        #j = json.loads(data.decode("utf-8"))
        #print("data: " + data.decode("utf-8"))
        drive_lock.acquire()
        try:
            events = 0
            for event in gamepad.read_loop():
                if event.type == ecodes.EV_ABS:
                    absevent = categorize(event)
                    #print(ecodes.bytype[absevent.event.type][absevent.event.code], absevent.event.value)
                    if ecodes.bytype[absevent.event.type][absevent.event.code] == "ABS_Y":
                        speed = math.floor(100 - (absevent.event.value - 8300) / ( 59000 - 8300 ) * 100)
                        events += 1
                    elif ecodes.bytype[absevent.event.type][absevent.event.code] == "ABS_RX":
                        angle = 180 - math.floor((absevent.event.value - 4300) / ( 53000 - 4300 ) * 180)
                        events += 1
                if events > 10:
                    break # too many events geeze
        finally:
            drive_lock.release()

        #speed = int(j['speed'])
        #angle = int(j['angle'])
    return


setup_multicast()
setup()
drive()

drive_lock = threading.Lock()
speed = 0
angle = 90

multicast_thread = threading.Thread(target = receive_multicast)
multicast_thread.daemon = True
multicast_thread.start()

signal.signal(signal.SIGINT, signal_handler)

# Wait 5 seconds on debugger mode
remaining = 100
old_speed = 0
old_angle = 90
speed = 0

if args.debug:
    speed = 100
while not args.debug or args.debug and remaining > 0:
    drive_lock.acquire()
    try:
        if old_speed != speed:
            drive(speed)
            print("speed: " + str(speed) + ", angle: " + str(angle))
            old_speed = speed
        if old_angle != angle:
            turn(angle)
            print("speed: " + str(speed) + ", angle: " + str(angle))
            old_angle = angle
    finally:
        drive_lock.release()
    if args.debug: print("remaining time: " + str(remaining / 10))
    time.sleep(.1)
    if args.debug: remaining-=1

cleanup()
