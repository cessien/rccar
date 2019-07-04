#import evdev
from evdev import InputDevice, categorize, ecodes

#creates object 'gamepad' to store the data
#you can call it whatever you like
gamepad = InputDevice('/dev/input/event0')

#prints out device info at start
print(gamepad)

#evdev takes care of polling the controller in a loop
for event in gamepad.read_loop():
    print(categorize(event))
    if event.type == ecodes.EV_ABS:
        absevent = categorize(event)
        print(ecodes.bytype[absevent.event.type][absevent.event.code], absevent.event.value)
