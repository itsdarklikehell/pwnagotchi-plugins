#! /usr/bin/python
#
# gpsfake -- test harness for gpsd
#
# Simulates one or more GPSes, playing back logfiles.
# Most of the logic for this now lives in gps.fake,
# factored out so we can write other test programs with it.
#
# This file is Copyright (c) 2010 by the GPSD project
# BSD terms apply: see the file COPYING in the distribution root for details.

# This code runs compatibly under Python 2 and 3.x for x >= 2.
# Preserve this property!
from __future__ import absolute_import, print_function, division

import getopt
import os
import platform
import pty
import socket
import sys
import time

import gps
import gps.fake as gpsfake   # The "as" pacifies pychecker

try:
    my_input = raw_input
except NameError:
    my_input = input

# Get version of stdout for bytes data (NOP in Python 2)
bytesout = gps.get_bytes_stream(sys.stdout)


class Baton(object):
    "Ship progress indications to stderr."
    # By setting this > 1 we reduce the frequency of the twirl
    # and speed up test runs.  Should be relatively prime to the
    # nunber of baton states, otherwise it will cause beat artifacts
    # in the twirling.
    SPINNER_INTERVAL = 11

    def __init__(self, prompt, endmsg=None):
        self.stream = sys.stderr
        self.stream.write(prompt + "...")
        if os.isatty(self.stream.fileno()):
            self.stream.write(" \b")
        self.stream.flush()
        self.count = 0
        self.endmsg = endmsg
        self.time = time.time()
        return

    def twirl(self, ch=None):
        if self.stream is None:
            return
        if os.isatty(self.stream.fileno()):
            if ch:
                self.stream.write(ch)
                self.stream.flush()
            elif self.count % Baton.SPINNER_INTERVAL == 0:
                self.stream.write("-/|\\"[self.count % 4])
                self.stream.write("\b")
                self.stream.flush()
        self.count = self.count + 1
        return

    def end(self, msg=None):
        if msg is None:
            msg = self.endmsg
        if self.stream:
            self.stream.write("...(%2.2f sec) %s.\n"
                              % (time.time() - self.time, msg))
        return


def hexdump(s):
    rep = ""
    for c in s:
        rep += "%02x" % ord(c)
    return rep


def fakehook(linenumber, fakegps):
    if len(fakegps.testload.sentences) == 0:
        sys.stderr.write("fakegps: no sentences in test load.\n")
        raise SystemExit(1)
    if linenumber % len(fakegps.testload.sentences) == 0:
        if singleshot and linenumber > 0:
            return False
        if progress:
            baton.twirl('*\b')
        elif not singleshot:
            if not quiet:
                sys.stderr.write("gpsfake: log cycle of %s begins.\n"
                                 % fakegps.testload.name)
    time.sleep(cycle)
    if linedump and fakegps.testload.legend:
        ml = fakegps.testload.sentences[
            linenumber % len(fakegps.testload.sentences)].strip()
        if not fakegps.testload.textual:
            ml = hexdump(ml)
        announce = fakegps.testload.legend \
            % (linenumber % len(fakegps.testload.sentences) + 1) + ml
        if promptme:
            my_input(announce + "? ")
        else:
            print(announce)
    if progress:
        baton.twirl()
    return True

if __name__ == '__main__':
    try:
        (options, arguments) = getopt.getopt(sys.argv[1:],
                                             "1bc:D:ghilm:no:pP:qr:s:StTuvx")
    except getopt.GetoptError as msg:
        print("gpsfake: " + str(msg))
        raise SystemExit(1)

    port = None
    progress = False
    cycle = 0.0
    monitor = ""
    speed = 4800
    linedump = False
    predump = False
    pipe = False
    singleshot = False
    promptme = False
    client_init = '?WATCH={"json":true,"nmea":true}'
    doptions = ""
    tcp = False
    udp = False
    verbose = 0
    slow = False
    quiet = False
    for (switch, val) in options:
        if switch == '-1':
            singleshot = True
        elif switch == '-b':
            progress = True
        elif switch == '-c':
            cycle = float(val)
        elif switch == '-D':
            doptions += " -D " + val
        elif switch == '-g':
            monitor = "xterm -e gdb -tui --args "
        elif switch == '-i':
            linedump = promptme = True
        elif switch == '-l':
            linedump = True
        elif switch == '-m':
            monitor = val + " "
        elif switch == '-n':
            doptions += " -n"
        elif switch == '-x':
            predump = True
        elif switch == '-o':
            doptions = val
        elif switch == '-p':
            pipe = True
        elif switch == '-P':
            port = int(val)
        elif switch == '-q':
            quiet = True
        elif switch == '-r':
            client_init = val
        elif switch == '-s':
            speed = int(val)
        elif switch == '-S':
            slow = True
        elif switch == '-t':
            tcp = True
        elif switch == '-T':
            sys.stdout.write("sys %s platform %s: WRITE_PAD = %.5f\n"
                             % (sys.platform, platform.platform(),
                                gpsfake.GetDelay(slow)))
            raise SystemExit(0)
        elif switch == '-u':
            udp = True
        elif switch == '-v':
            verbose += 1
        elif switch == '-h':
            sys.stderr.write("usage: gpsfake"
                             " [-1] [-h] [-i] [-l] [-g] [-q] [-m monitor]"
                             " [-D debug] [-n] [-o options] [-p]\n"
                             "\t[-P port] [-r initcmd] [-t] [-T] [-v] [-x]"
                             " [-s speed] [-S] [-c cycle] [-b] logfile...\n")
            raise SystemExit(0)

    try:
        pty.openpty()
    except (AttributeError, OSError):
        sys.stderr.write("gpsfake: ptys not available, falling back to UDP.\n")
        udp = True

    if not arguments:
        sys.stderr.write("gpsfake: requires at least one logfile argument.\n")
        raise SystemExit(1)

    if progress:
        baton = Baton("Processing %s" % ",".join(arguments), "done")
    elif not quiet:
        sys.stderr.write("Processing %s\n" % ",".join(arguments))

    # Don't allocate a private port when cycling logs for client testing.
    if port is None and not pipe:
        port = int(gps.GPSD_PORT)

    test = gpsfake.TestSession(prefix=monitor, port=port, options=doptions,
                               tcp=tcp, udp=udp, verbose=verbose,
                               predump=predump, slow=slow)

    if pipe:
        test.reporter = bytesout.write
        if verbose:
            progress = False
            test.progress = sys.stderr.write
    
    # Create a special character file that acts like a GPS device, but is really a shitty GSM hat.    
    special_file = test.gsm_gps_add(arguments[0], speed=speed, pred=fakehook, oneshot=singleshot)
    
    print("[+] Set bettercap gps.device value to: {}".format(special_file))
    test.run()

# The following sets edit modes for GNU EMACS
# Local Variables:
# mode:python
# End:
