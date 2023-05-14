#!/usr/bin/python3

# this script waits for pressed button at soundcard https://www.raspiaudio.com/promo and clean shutdown the raspberry pi
#
# edit "/etc/rc.local" and add the line "cd /usr/local/pwnagotchi/plugins/sound/ ; ./shutdown_button.py &" before the "exit 0" line


import logging
import os, subprocess
import RPi.GPIO as GPIO

logging.basicConfig(
    filename='/var/log/pwnagotchi-shutdown.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
    )


GPIO.setmode(GPIO.BCM)
# 23 is the button on sound card
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        # wait for the pin to be sorted with GND and, if so, halt the system
        GPIO.wait_for_edge(23, GPIO.FALLING)
        # speak
        os.system('pico2wave -l en-US -w stdout.wav "system is shutting down" | aplay -q --')
        # shut down the rpi
        logging.info("shutdown pressed");
        os.system("/sbin/shutdown -h now")
except:
    logging.info("exception!");
    GPIO.cleanup()
