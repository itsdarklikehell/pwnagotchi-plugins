import logging
import struct
import RPi.GPIO as GPIO
import sys
import time
# Import wraps for the decorator
from functools import wraps

sys.path.append('/usr/local/share/pwnagotchi') # May not be needed
import pwnagotchi
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK

try:
    import smbus
except ImportError:
    logging.error("UPSLite plugin requires smbus. Run 'sudo apt install python3-smbus'")
    smbus = None

CW2015_ADDRESS   = 0X62
CW2015_REG_VCELL = 0X02
CW2015_REG_SOC   = 0X04
CW2015_REG_MODE  = 0X0A
CW2015_QUICKSTART_VAL = 0x30
GPIO_PIN_CHARGING = 4

log = logging.getLogger('pwnagotchi_plugins')

def handle_errors(log_func, default_value):
    """
    Decorator factory to handle common errors (I2C, General) in UPS methods,
    log them, and return a default value.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs): # Added 'self' to work with instance methods
            try:
                return func(self, *args, **kwargs) # Pass 'self' to the wrapped method
            except IOError as e:
                # Log I2C errors - use the provided log function (e.g., log.debug or log.error)
                log_func("UPSLite: I2C Error in %s: %s", func.__name__, e)
                return default_value
            except Exception as e:
                # Log other unexpected errors
                log.error("UPSLite: Unexpected error in %s: %s", func.__name__, e, exc_info=True) # Use log.error and add traceback
                return default_value
        return wrapper
    return decorator

class UPS:
    def __init__(self):
        if smbus is None:
             raise ImportError("smbus library not found for UPS class")
        self._bus = smbus.SMBus(1)
        self._quickstart() # Initialize the chip ONCE here

        # Setup GPIO - do it once here
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(GPIO_PIN_CHARGING, GPIO.IN)
            log.debug("UPSLite: GPIO %d setup OK.", GPIO_PIN_CHARGING)
        except Exception as e:
            # Let this error propagate during init, or handle differently if needed
            log.error("UPSLite: Error setting up GPIO %d: %s", GPIO_PIN_CHARGING, e, exc_info=True)
            # Consider if the plugin should load if GPIO fails - maybe it should?

    # _quickstart still needs its own specific error handling as it doesn't return a value
    def _quickstart(self):
        """Wakes up the CW2015 and triggers calculations."""
        try:
            self._bus.write_byte_data(CW2015_ADDRESS, CW2015_REG_MODE, CW2015_QUICKSTART_VAL)
            log.info("UPSLite: CW2015 QuickStart command sent (wrote 0x%02X to 0x%02X)", CW2015_QUICKSTART_VAL, CW2015_REG_MODE)
            time.sleep(0.1)
        except IOError as e:
            log.error("UPSLite: I2C Error sending QuickStart command: %s", e)
        except Exception as e:
            log.error("UPSLite: Unexpected error during QuickStart: %s", e, exc_info=True)

    # Apply the decorator to voltage method
    @handle_errors(log.debug, 0.0) # Use log.debug for frequent I2C errors, default 0.0
    def voltage(self):
        """Reads voltage. Returns voltage in V or 0.0 on error."""
        # Removed try/except block - decorator handles it
        read = self._bus.read_word_data(CW2015_ADDRESS, CW2015_REG_VCELL)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        voltage = swapped * 0.305 / 1000 # Correct scale factor
        return voltage

    # Apply the decorator to capacity method
    @handle_errors(log.debug, 0.0) # Use log.debug for frequent I2C errors, default 0.0
    def capacity(self):
        """Reads capacity percentage. Returns % (0-100) or 0.0 on error."""
        # Removed try/except block - decorator handles it
        read = self._bus.read_word_data(CW2015_ADDRESS, CW2015_REG_SOC)
        swapped = struct.unpack("<H", struct.pack(">H", read))[0]
        capacity = swapped / 256.0 # Correct calculation
        return max(0.0, min(100.0, capacity)) # Clamp value

    # Apply the decorator to charging method
    @handle_errors(log.error, '?') # Use log.error for GPIO errors, default '?'
    def charging(self):
        """Checks charging status via GPIO. Returns '+' (charging), '-' (discharging), or '?' (error)."""
        # Removed try/except block - decorator handles it
        # Note: This decorator won't catch the initial GPIO setup error in __init__
        return '+' if GPIO.input(GPIO_PIN_CHARGING) == GPIO.HIGH else '-'


# The UPSLite plugin class remains the same as the previous version
class UPSLite(plugins.Plugin):
    __author__ = 'evilsocket@gmail.com, LouD, dlmd, Juan_milano@hotmail.com'
    __version__ = '1.0.4' # Incremented version for decorator refactoring
    __license__ = 'GPL3'
    __description__ = 'A plugin that displays battery capacity/charging for UPS Lite v1.3 (CW2015) and supports auto-shutdown with improved error handling via decorator.'
    __defaults__ = {
        'enabled': False,
        'shutdown': 5,
    }

    # ... (__init__, on_loaded, on_ui_setup, on_unload methods remain the same
    #      as the previous version with the outer try/except in on_ui_update) ...
    def __init__(self):
        self.ups = None
        self.shutdown_threshold = 5
        log.debug("UPSLite plugin __init__")

    def on_loaded(self):
        log.info("UPSLite plugin loaded")
        try:
            cfg_shutdown = self.options.get('shutdown', self.__defaults__['shutdown'])
            if isinstance(cfg_shutdown, int) and 0 <= cfg_shutdown <= 100:
                 self.shutdown_threshold = cfg_shutdown
            else:
                 log.warning("UPSLite: Invalid shutdown value in config (%s), using default %d%%", cfg_shutdown, self.__defaults__['shutdown'])
                 self.shutdown_threshold = self.__defaults__['shutdown']

            self.ups = UPS()
            log.info("UPSLite: UPS object initialized successfully. Shutdown threshold: %d%%", self.shutdown_threshold)
        except Exception as e:
            log.error("UPSLite: Failed to initialize UPS object: %s", e, exc_info=True)
            self.ups = None

    def on_ui_setup(self, ui):
        try:
            log.debug("UPSLite: Setting up UI element 'ups'")
            ui.add_element('ups', LabeledValue(color=BLACK, label='UPS', value='--', position=(ui.width() // 2 + 15, 0),
                                               label_font=fonts.Bold, text_font=fonts.Medium))
        except Exception as e:
            log.error("UPSLite: Error setting up UI: %s", e, exc_info=True)

    def on_unload(self, ui):
        try:
            log.info("UPSLite plugin unloaded")
            with ui._lock:
                if 'ups' in ui._state._state:
                     ui.remove_element('ups')
        except Exception as e:
            log.error("UPSLite: Error during unload: %s", e, exc_info=True)

    # on_ui_update still benefits from its outer try/except block
    def on_ui_update(self, ui):
        try: # Outer block for overall method safety
            if self.ups:
                # No inner try/except needed here now, decorator handles method errors
                capacity = self.ups.capacity() # Will return 0.0 on error
                charging = self.ups.charging() # Will return '?' on error
                capacity_int = int(round(capacity))

                # Handle potential '?' from charging error if needed
                display_charging = charging if charging in ['+', '-'] else '-' # Default to '-' if error '?'

                ui.set('ups', "%2i%%%s" % (capacity_int, display_charging))

                # Check for shutdown condition ONLY if not charging (and no charging error)
                if charging == '-': # Only shutdown if definitively discharging
                    if capacity_int <= self.shutdown_threshold:
                        log.warning('[UPSLite] Low battery (%.1f%% <= %d%%) and not charging: shutting down!', capacity, self.shutdown_threshold)
                        try:
                            ui.set('ups', "%2i%%%s" % (capacity_int, display_charging))
                            ui.update(force=True, new_data={'status': 'Battery low (%d%%), shutting down...' % capacity_int})
                            time.sleep(2)
                        except Exception as ui_e:
                            log.error("UPSLite: Failed to update UI before shutdown: %s", ui_e)
                        pwnagotchi.shutdown()

            else: # self.ups is None
                 try:
                     ui.set('ups', "--")
                 except Exception as e_ui_else:
                     log.error("UPSLite: Failed to set UI to default '--' state: %s", e_ui_else)

        except Exception as e_outer:
            log.error("UPSLite: Unhandled exception in on_ui_update: %s", e_outer, exc_info=True)
