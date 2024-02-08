import logging
import signal
import sys
import threading
import time
import os
import RPi.GPIO as GPIO

import numpy as np

from subprocess import Popen, PIPE, check_output

import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import *
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts


class Touch_Button(Widget):
    def __init__(
        self,
        position=(0, 0, 30, 30),
        color="White",
        *,
        state=False,
        momentary=False,
        reverse=False,
        text=None,
        value=None,
        text_color="Black",
        font=None,
        image=None,
        shadow="Black",
        highlight="White",
        outline=None,
        alt_text=None,
        alt_text_color=None,
        alt_font=None,
        alt_image=None,
        alt_color=None,
        event_handler=None,
    ):

        super().__init__(position, color)
        self.event_handler = event_handler  # callback events, press, release
        self.xy = position
        self.color = color
        self.state = state  # False=off, True=on
        self.momentary = momentary  # False = toggle on/off, True  = on while pressed, off on release (single action)
        self.reverse = (
            reverse  # if True, then default state is True, and alt state is False
        )

        self.shadow = shadow  # on "falling" sides of button
        self.highlight = highlight  # on "rising" sides of button
        self.outline = outline  # outer ring of button, drawn last

        self.text = text  # text label
        self.value = value  # default value (if set, displayed under text)
        self.text_color = text_color  # default text_color
        self.font = font  # default font (None)
        if image:
            try:
                self.image = Image.open(image)
            except Exception as e:
                logging.warn("Image %s error: %s" % (image, repr(e)))
                self.image = None
        else:
            self.image = None  # default image (None)

        # alternate display items for pressed state
        self.alt_color = alt_color
        self.alt_text_color = alt_text_color if alt_text_color else text_color
        self.alt_text = alt_text
        self.alt_font = alt_font if alt_font else font
        if alt_image:
            try:
                self.alt_image = Image.open(alt_image)
            except Exception as e:
                logging.warn("Image %s error: %s" % (alt_image, repr(e)))
                self.alt_image = None
        else:
            self.alt_image = None  # default image (None)

    def draw(self, canvas, drawer):
        try:
            pressed = self.state != self.reverse
            xy = np.array(self.xy)

            # draw button highlight and shadow
            if pressed:
                upper = list(np.add(xy, np.array([-1, -1, 0, 0])))
                drawer.rectangle(upper, fill=self.highlight)
            else:
                lower = list(np.add(xy, np.array([2, 2, 1, 1])))
                drawer.rectangle(lower, fill=self.shadow)
                xy = np.add(xy, np.array([-1, -1, -1, -1]))

            # draw button background
            color = self.alt_color if pressed and self.alt_color else self.color
            drawer.rectangle(list(xy), fill=color, outline=self.outline)

            image = self.alt_image if pressed and self.alt_image else self.image
            if image:
                canvas.paste(image, list(xy))

            text = self.alt_text if pressed and self.alt_text else self.text

            value = self.value

            if value:
                if text:
                    text = "%s\n%s" % (text, value)
                else:
                    text = "%s" % value

            text_color = self.alt_text_color if pressed else self.text_color
            text_font = self.alt_font if pressed else self.font

            if text:
                textpos = ((xy[0] + xy[2]) / 2, (xy[1] + xy[3]) / 2 + 1)
                drawer.text(
                    textpos,
                    text,
                    anchor="mm",
                    fill=text_color,
                    font=text_font,
                    align="center",
                )

            # if self.outline:
            #    drawer.rectangle(list(np.add(xy, np.array([-1,-1,1,1]))), outline = self.outline)

        except Exception as e:
            logging(repr(e))


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


@singleton
class Touch_Screen(plugins.Plugin):
    __author__ = "SgtStroopwafel, Sniffleupagus"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "Use touchscreen input to toggle settings."

    # Touch screen support
    #
    # uses system touchscreens in /dev/input/event*
    #
    # Requires tslib and evtest:
    #
    #  % sudo apt install evtest libts-bin
    #
    # Tested with Waveshare Touch 2.13 E-paper HAT
    # - add to /boot/config.txt:  dtoverlay=goodix,interrupt=27,reset=22
    # - pwnagotchi display is "waveshare_v3"
    #
    # Tested with Inland 3.5" TFT touchscreen, 26-pin connector
    # - install https://github.com/goodtft/LCD-show
    #
    #
    #
    # plugins that want to receive touch events can implement these callback functions:
    #
    ## on_touch_ready(self, touchscreen)
    #
    # - called when the touchscreen has been started. Your plugin can use it to know the touchscreen
    #   is available.
    #
    ## on_touch_press(self, ts, ui, ui_element, touch_data)
    ## on_touch_release(self, ts, ui, ui_element, touch_data)
    #
    # # simplified button-like interface. on_touch_press is the initial touch,
    # # then supress all the wiggling, and on_touchs_release is the "0" when
    # # your finger comes off the screen. Much more efficient, if you are just pressing
    # # something to do an action
    #
    ## on_touch_move(self, ts, ui, ui_element, touch_data)
    #
    # # This will get every position update between the press and release (every finger wiggle).
    # # alsmost raw touchscreen access. This does not get called for the press or release, just
    # # all the in-betweens.
    #
    # # variables:
    #
    #   self = your plugin instance
    #
    #   ts, touchscreen = this touchscreen plugin instance
    #
    #   ui = pwnagotchi view/ui like in other plugin handlers
    #
    #   ui_element = name of display element where touch occurred. NOT IMPLEMENTED YET!!!!!
    #
    #   touch_data = { point: [x,y], pressure: p }
    #     x,y = point of touch
    #     p = 1-255 how hard being pressed
    #         0 when released
    #
    #
    # Future improvements:
    #
    # - make an array called Touch_Elements listing the UI elements of interest
    #
    # self.Touch_Elements = [ "face", "uptime", "assoc_count", "deauth_count" ]
    #
    # if a touch event occurs inside a ui_element in a plugin's Touch_Elements array,
    # on_touch* will get called (to all plugins implementing it, so check the element before blindly
    # processing a touch

    # - if user has buttons available, one can be assigned "next" to cycle through the touchable areas, highlighting
    # the current one with a box or something. If another button assigned to "ok"  is pressed, it is considered
    # a touch event on the selected item, and a touch release (0) event when the button is released. "prev" to cycle
    # backwares and "back" (just dismisses highlighting the selected element for now) are also implemented for UI
    # navigation.
    # - web_ui to add/remove UI elements from button cycling

    def __init__(self):
        self.running = False
        self._ts_thread = None  # ts_print thread
        self.keepGoing = (
            False  # let the ts_print thread know to stop going when we exit
        )
        self._view = None  # pwnagotchi view/ui/display
        self._agent = None  # pwnagotchi agent
        self._beingTouched = False  # currently being touched or not
        self._ui_elements = (
            []
        )  # keep track of UI elements created in on_ui_setup for easy removal in on_unload

        self.touchscreen = None  # ts_print external process

        self.touch_elements = {}  # ui elements of interest for touch events

        self.needsAptPackages = None

        # use buttons to cycle through user elements
        # web_ui to select which ones to include or not include
        self.buttonCurrentZone = None

        logging.basicConfig(
            format="%(asctime)-15s %(levelname)s [%(filename)s:%(lineno)d] %(funcName)s: %(message)s"
        )

        logging.debug("plugin created")

    def touchScreenHandler(self, ts_device=None):
        try:
            if not ts_device:
                # try to find a touchscreen device
                evtest = Popen(
                    ("/usr/bin/evtest"),
                    stdout=PIPE,
                    stderr=PIPE,
                    universal_newlines=True,
                )
                if not evtest:
                    self.needsAptPackages = ["evtest", "libts-bin"]

                while True:
                    output = str(evtest.stderr.readline())
                    if not output:
                        break
                    output.rstrip("\n")
                    logging.info("Looking for screen: %s" % repr(output))
                    try:
                        if "touchscreen" in output.lower():
                            (ts_device, rest) = output.split(":", 2)
                            ts_device = str(ts_device)
                            logging.info("Found touchscreen device %s" % ts_device)
                            break
                    except Exception as e:
                        logging.error(repr(e))

            self.keepGoing = True
            while ts_device and self.keepGoing:
                cmd = "/usr/bin/ts_print"
                os.environ["TSLIB_TSDEVICE"] = "%s" % ts_device
                self.touchscreen = (
                    Popen(
                        ["stdbuf", "-o0", cmd],
                        env=os.environ,
                        stdout=PIPE,
                        universal_newlines=True,
                        shell=False,
                    )
                    if not self.needsAptPackages
                    else None
                )

                if self.touchscreen:
                    logging.info("ts_print running")
                    self.running = True
                    for output in self.touchscreen.stdout:
                        if not output or not self.keepGoing:
                            break
                        output = output.strip()
                        logging.debug("Touch '%s'" % output)
                        (tstamp, y, x, depth) = output.split()
                        x = int(x)
                        y = int(y)

                        rotation = (
                            self._agent._config["ui"]["display"]["rotation"]
                            if self._agent
                            else 180
                        )

                        if (
                            rotation == 180
                        ):  # 0,0 is top left, but touch screen 0,0 is bottom left
                            x = self._view._width - x
                        else:
                            y = self._view._height - y

                        depth = int(depth)
                        if tstamp:
                            logging.debug("Touch %s at %s, %s" % (depth, x, y))
                            self.process_touch([int(x), int(y)], depth)
                    logging.info("ts_print exited")
                    self.running = False
                else:
                    logging.info("No touchscreen?")
                    self.needsAptPackages = ["evtest", "libts-bin"]
                time.sleep(1)

            # err = self.touchscreen.stderr.read()
            # logging.info(err)
        except Exception as e:
            logging.info("Handler: %s" % repr(e))

    def on_webhook(self, path, request):
        # define which elements are active or not
        # show pwny image. send clicks through
        pass

    # called when the plugin is loaded
    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")
        logging.info("loaded with options = " % self.options)

        # to test pimoroni displayhatmini buttons, uncomment below, or define in your config.toml
        ##if 'gpios' not in self.options:
        ##    self.options['gpios'] = {'ok': 6, 'back' : 5, 'next': 24, 'prev': 16}   # Pimoroni display hat mini
        try:
            self.init_gpio()
        except Exception as e:
            logging.warn(repr(e))

        # start touch screen background thread
        try:
            self.init_ts_handler()
        except Exception as e:
            logging.warn(repr(e))

        # notify plugins
        plugins.on("touch_ready", self)

    # called before the plugin is unloaded
    def on_unload(self, ui):
        try:
            # stop the thread
            self.keepGoing = False
            if self._ts_thread:
                if self.touchscreen:
                    logging.debug("TERM to %s" % self.touchscreen.pid)
                    os.kill(self.touchscreen.pid, signal.SIGTERM)
                logging.debug("Waiting for thread to exit")
                self._ts_thread.join()
                logging.info("And its done.")
        except Exception as e:
            logging.error("%s" % repr(e))

        try:
            # remove UI elements
            i = 0
            for n in self._ui_elements:
                ui.remove_element(n)
                logging.info("Removed %s" % repr(n))
                i += 1
            if i:
                logging.info("plugin unloaded %d elements" % i)

        except Exception as e:
            logging.error("%s" % repr(e))

        try:
            if "gpios" in self.options:
                for i in self.options["gpios"].values():
                    logging.info("Stop detecting GPIO %s" % repr(i))
                    GPIO.remove_event_detect(i)

        except Exception as e:
            logging.error("%s" % repr(e))

    # called when there's internet connectivity - probably dont need this
    def on_internet_available(self, agent):
        if self.needsAptPackages:
            check_output(["apt", "install", "-y"].extend(self.needsAptPackages))
            self.needsAptPackages = None

    # is this point(x,y) in box (x1, y1, x2, y2), x2>x1, y2>y1
    def pointInBox(self, point, box):
        try:
            logging.debug("is %s in %s" % (repr(point), repr(box)))
            return (
                point[0] >= box[0]
                and point[0] <= box[2]
                and point[1] >= box[1]
                and point[1] <= box[3]
            )
        except Exception as e:
            logging.info(repr(e))

    def collect_touch_elements(self):
        # - go through plugins, and build touch_elements cache and complete array
        #   - cache is a mapping of plugin to touch_elements
        # - in process_touch, compare each plugin touch_elements to cached, and update if changed
        # - cache bounding boxes of elements, indexed on "name:xy:font:value", and update when
        #   different
        # Any display elements listed in the array will be checked for _press and _release,
        # and be available for button presses.
        pass

    def process_touch(self, tpoint, depth):
        logging.info("PT: %s: %s" % (repr(tpoint), repr(depth)))

        touch_data = {"point": tpoint, "pressure": depth}

        # check UI element bounding boxes and call on_touch
        ui_elements = self._view._state._state
        touch_element = None
        touch_elements = list(
            filter(lambda x: hasattr(ui_elements[x], "state"), ui_elements.keys())
        )
        logging.info("Touchable: %s" % repr(touch_elements))
        try:
            if int(depth) > 0:
                command = "touch_move" if self._beingTouched else "touch_press"
                self._beingTouched = True
            elif int(depth) == 0:
                command = "touch_release"
                self._beingTouched = False
            else:
                command = None

            for te in touch_elements:
                logging.info("Touching %s, %s" % (te, repr(ui_elements[te].xy)))
                if self.pointInBox(tpoint, ui_elements[te].xy):
                    logging.debug(
                        "Touch element %s: %s @ %s" % (repr(te), depth, repr(tpoint))
                    )
                    touch_element = te
                    break  # stop at first match

        except Exception as e:
            logging.warn(repr(e))

        if command:
            if touch_element:
                button = ui_elements[touch_element]
                if button.momentary:
                    if command == "touch_press" or command == "touch_release":
                        self._view._state._changes[touch_element] = True
                    button.state = self._beingTouched
                    if reverse:
                        button.state = not button.state
                elif command == "touch_press":
                    button.state = not button.state
                    self._view._state._changes[touch_element] = True

                if hasattr(ui_elements[touch_element], "event_handler"):
                    logging.info(
                        "UI_Element %s Command: %s, handler: %s, data: %s"
                        % (
                            touch_element,
                            command,
                            ui_elements[touch_element].event_handler,
                            repr(touch_data),
                        )
                    )
                    plugins.one(
                        ui_elements[touch_element].event_handler,
                        command,
                        self,
                        self._view,
                        touch_element,
                        touch_data,
                    )
                else:
                    logging.info(
                        "UI_Element %s Command: %s, handler: %s, data: %s"
                        % (
                            touch_element,
                            command,
                            ui_elements[touch_element].event_handler,
                            repr(touch_data),
                        )
                    )
                    plugins.on(command, self, self._view, touch_element, touch_data)

            else:
                logging.debug(
                    "Touch Command: %s, data: %s" % (command, repr(touch_data))
                )
                plugins.on(command, self, self._view, touch_element, touch_data)

    # button handlers to cycle through touch areas and click
    # just detect clicks for now, NOT IMPLEMENTED YET
    def okButtonPress(self, button):
        logging.info("OK Button pressed: %s" % repr(button))
        if self.buttonCurrentZone:
            # find center, and highlight element
            pass

    def okButtonRelease(self, button):
        logging.info("OK Button released: %s" % repr(button))
        if self.buttonCurrentZone:
            # find center, and process click
            pass

    def backButtonPress(self, button):
        logging.info("Back Button pressed: %s" % repr(button))
        if self.buttonCurrentZone:
            # remove highlight and unselect
            self.buttonCurrentZone = None
            pass

    def backButtonRelease(self, button):
        logging.info("Back Button released: %s" % repr(button))
        if self.buttonCurrentZone:
            # remove highlight and unselect
            self.buttonCurrentZone = None
            pass

    def nextButtonPress(self, button):
        logging.info("Next Button pressed: %s" % repr(button))
        if self.buttonCurrentZone:
            # pick the next one
            pass
        else:
            # pick the first one, or last used one?
            pass

    def nextButtonRelease(self, button):
        logging.info("Next Button released: %s" % repr(button))
        if self.buttonCurrentZone:
            # pick the next one
            pass
        else:
            # pick the first one, or last used one?
            pass

    def prevButtonPress(self, button):
        logging.info("Prev Button pressed: %s" % repr(button))
        if self.buttonCurrentZone:
            # pick the previous one
            pass

    def prevButtonRelease(self, button):
        logging.info("Prev Button released: %s" % repr(button))
        if self.buttonCurrentZone:
            # pick the previous one
            pass

    # called when the hardware display setup is done, display is an hardware specific object
    def on_display_setup(self, display):
        # touchscreen setup/connection should go here, but doesn't have agent.. just display...
        pass

    # called when everything is ready and the main loop is about to start
    def on_ready(self, agent):
        self._agent = agent  # save for posterity

    def init_gpio(self):
        # set up GPIO - next, previous, ok, back
        if "gpios" in self.options:
            GPIO.setmode(GPIO.BCM)
            if "ok" in self.options["gpios"]:
                try:
                    GPIO.setup(int(self.options["gpios"]["ok"]), GPIO.IN, GPIO.PUD_UP)
                    GPIO.add_event_detect(
                        int(self.options["gpios"]["ok"]),
                        GPIO.FALLING,
                        callback=self.okButtonPress,
                        bouncetime=600,
                    )
                    GPIO.add_event_detect(
                        int(self.options["gpios"]["ok"]),
                        GPIO.RISING,
                        callback=self.okButtonRelease,
                        bouncetime=600,
                    )
                except Exception as err:
                    logging.warn("OK button: %s" % repr(err))
            if "next" in self.options["gpios"]:
                try:
                    GPIO.setup(int(self.options["gpios"]["next"]), GPIO.IN, GPIO.PUD_UP)
                    GPIO.add_event_detect(
                        int(self.options["gpios"]["next"]),
                        GPIO.FALLING,
                        callback=self.nextButtonPress,
                        bouncetime=600,
                    )
                    GPIO.add_event_detect(
                        int(self.options["gpios"]["next"]),
                        GPIO.RISING,
                        callback=self.nextButtonRelease,
                        bouncetime=600,
                    )
                except Exception as err:
                    logging.warn("Next button: %s" % repr(err))
            if "back" in self.options["gpios"]:
                try:
                    GPIO.setup(int(self.options["gpios"]["back"]), GPIO.IN, GPIO.PUD_UP)
                    GPIO.add_event_detect(
                        int(self.options["gpios"]["back"]),
                        GPIO.FALLING,
                        callback=self.backButtonPress,
                        bouncetime=600,
                    )
                    GPIO.add_event_detect(
                        int(self.options["gpios"]["back"]),
                        GPIO.RISING,
                        callback=self.backButtonRelease,
                        bouncetime=600,
                    )
                except Exception as err:
                    logging.warn("Back button: %s" % repr(err))
            if "prev" in self.options["gpios"]:
                try:
                    GPIO.setup(int(self.options["gpios"]["prev"]), GPIO.IN, GPIO.PUD_UP)
                    GPIO.add_event_detect(
                        int(self.options["gpios"]["prev"]),
                        GPIO.FALLING,
                        callback=self.prevButtonPress,
                        bouncetime=600,
                    )
                    GPIO.add_event_detect(
                        int(self.options["gpios"]["prev"]),
                        GPIO.RISING,
                        callback=self.prevButtonRelease,
                        bouncetime=600,
                    )
                except Exception as err:
                    logging.warn("Prev button: %s" % repr(err))

    def init_ts_handler(self):
        # start touchscreen handler thread
        try:
            logging.debug("starting ts_print thread")
            self._ts_thread = threading.Thread(
                target=self.touchScreenHandler, args=(), daemon=True
            )
            if not self._ts_thread:
                logging.info("Thread failed?")

            # self.touchScreenHandler()
            logging.debug("starting ts_print thread")
            self._ts_thread.start()
            logging.info("started thread")

            logging.info("unit is ready")
        except Exception as e:
            logging.error(repr(e))

    # called to setup the ui elements
    def on_ui_setup(self, ui):
        self._view = ui
        # later, look through _view to get bounding boxes

    # called when the agent is rebooting the board
    def on_rebooting(self, agent):
        pass

    # called when the agent is waiting for t seconds
    def on_wait(self, agent, t):
        pass

    # called when the agent is sleeping for t seconds
    def on_sleep(self, agent, t):
        # update caches
        pass


if __name__ == "__main__":

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    # handler.setLevel(logging.DEBUG)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # handler.setFormatter(formatter)
    # root.addHandler(handler)

    ts = Touch_Screen()

    # ts.touchScreenHandler()

    ts.okButtonPress(69)
