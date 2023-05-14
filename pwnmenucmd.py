from multiprocessing.connection import Client
import sys

# Uncomment following 2 lines if using an active (self-oscillating) buzzer.
# Navigating the menu can be slow on an epaper display, so it helps to get
# feedback early when changing menu items.
#import RPi.GPIO as GPIO
#from time import sleep

# If using an active buzzer, change the following line to match your setup.
# eg. "buzzerpin = 5" for a buzzer attached to GPIO #5
# Setting this to zero will disable the buzzer.
buzzerpin = 0

if (len(sys.argv) != 2):
    print 'no menu command given. Try up/down/ok/back/close/stop'
    sys.exit()

cmd = sys.argv[1]
print 'cmd = ' + cmd
if cmd not in ('up', 'down', 'ok', 'back', 'close', 'stop'):
    print 'invalid menu command given. Try up/down/ok/back/close/stop'
    sys.exit()

if buzzerpin:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(buzzerpin, GPIO.OUT, initial=GPIO.LOW)
    GPIO.output(buzzerpin, GPIO.HIGH)
    sleep(0.025)
    GPIO.output(buzzerpin, GPIO.LOW)
    GPIO.cleanup() # Free up GPIO resources

address = ('localhost', 6789)
conn = Client(address)
conn.send(cmd)
conn.close()
