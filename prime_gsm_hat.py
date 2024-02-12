#!/usr/bin/python
import serial
import time
import RPi.GPIO as GPIO

"""
Assuming you're using the Waveshare Raspberry Pi GSM/GPRS/GNSS Bluetooth Hat for SIM868's I keep talking about:
    https://amazon.com/Raspberry-Bluetooth-Expansion-Compatible-DataTransfer/dp/B076CPX4NN

What it do, tho?
The setup_commands do the following, in order:
    1. Deactivate any existing bearer context
    2. Attach the GPRS services on the HAT module
    3. Set the bearer content type to GPRS
    4. Set the APN type to "default,supl,mms" (should work for most carriers, but google 'APN type' for your carrier, if not)
    5. Activate the configured bearer context
And then we're ready to fuck.

This script clearly doesn't do any sort of error, failure, or success checking, and I don't know
if I can be bothered to write any. I'm not going to make claims about my knowledge of this subject
matter; all I'm going to say is that it's complicated, ultra-specific, and will not work for anything
that even slightly deviates from the mashup of SIM800 and SIM900 commands available on the SIM868.
I haven't actually checked if this script works     XD

References that may help:
https://simcom.ee/documents/SIM800x/SIM800%20Series_GSM%20Location_Application%20Note_V1.01.pdf
https://www.cooking-hacks.com/media/cooking/images/documentation/tutorial-sim-908/SIM908_AT_Command_Manual_V1.02.pdf
https://simcom.ee/documents/SIM900/SIM900_GSM%20Location%20AT%20Command%20Manual_V1.00.pdf
https://github.com/stanleyhuangyc/Freematics/issues/17

"""
__GitHub__ = ""
__author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), Kaska"
__version__ = "1.1.0"
__license__ = "MIT"
__description__ = "use with gpsfake, to supply bettercap with better-than-nothing GPS coordinates from the GSM network. Use when stuck in and around glass/steel monoliths that eat GPS signals for breakfast. The provided coordinates are not only inaccurate because they come from second-hand means, but also because said means don't return elevation, so I put a hardcoded 100 in there because I don't know why. Really, I should focus on a more accurate 2d-fix over the 3d-fix, but I didn't. Requires the python gps modules (pip install gps) and pynmea2 for creating nice NMEA strings (pip install pynmea2). Make a backup of '/usr/lib/python2.7/dist-packages/gps/fake.py' and then replace it with the one provided (not totally necessary). Then run 'python prime_gsm_hat.py' to turn on the hat and start the GPRS data service. This only needs to be/should be run once per powering on of the hat. Next, run gsmfake.py using basic parameters used to start gpsfake: 'python gsmfake.py -P 2948 /root/fakegps.data'. Both fake.py and prime_gsm_hat.py have hardcoded paths to the Hat's serial IO, so keep that in mind. This will spit out a path like '/dev/pts/2' that you need to update bettercap with."
__name__ = "prime_gsm_hat"
__help__ = "use with gpsfake, to supply bettercap with better-than-nothing GPS coordinates from the GSM network. Use when stuck in and around glass/steel monoliths that eat GPS signals for breakfast. The provided coordinates are not only inaccurate because they come from second-hand means, but also because said means don't return elevation, so I put a hardcoded 100 in there because I don't know why. Really, I should focus on a more accurate 2d-fix over the 3d-fix, but I didn't. Requires the python gps modules (pip install gps) and pynmea2 for creating nice NMEA strings (pip install pynmea2). Make a backup of '/usr/lib/python2.7/dist-packages/gps/fake.py' and then replace it with the one provided (not totally necessary). Then run 'python prime_gsm_hat.py' to turn on the hat and start the GPRS data service. This only needs to be/should be run once per powering on of the hat. Next, run gsmfake.py using basic parameters used to start gpsfake: 'python gsmfake.py -P 2948 /root/fakegps.data'. Both fake.py and prime_gsm_hat.py have hardcoded paths to the Hat's serial IO, so keep that in mind. This will spit out a path like '/dev/pts/2' that you need to update bettercap with."
__dependencies__ = {
    "apt": ["none"],
    "pip": ["scapy"],
}
__defaults__ = {
    "enabled": False,
}

# I'm too lazy to care, so you figure it out. Powers on if not powered on.
if (
    not raw_input("Is the GSM/GPRS/GNSS hat powered on? [y/n]: ").lower().strip()[:1]
    == "y"
):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(7, GPIO.OUT)
    GPIO.output(7, GPIO.LOW)
    time.sleep(4)
    GPIO.output(7, GPIO.HIGH)
    GPIO.cleanup()

# AT commands:
deactivate_bearer_command = "AT+SAPBR=0,1"
setup_commands = [
    deactivate_bearer_command,
    "AT+CGATT=1",
    'AT+SAPBR=3,1,"Contype","GPRS"',
    'AT+SAPBR=3,1,"APN","default,supl,mms"',
    "AT+SAPBR=1,1",
]

try:
    # Open location of the GSM hat serial IO.
    serial_device = serial.Serial("/dev/ttyS0", 115200)

    for setup_command in setup_commands:
        print("[!] Running: " + setup_command)
        serial_device.write(setup_command + "\r\n")
        time.sleep(0.5)
        serial_device.flushInput()
    time.sleep(1)
    print("[+] Probably successfully primed GSM/GPRS/GNSS hat.")

except:
    print("[-] Encountered exception while writing to serial device.")

finally:
    # Aight, fine. A little help.
    if serial_device != None:
        serial_device.close()
