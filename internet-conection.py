import logging, os, pwnagotchi, urllib.request
import pwnagotchi.ui.components as components
import pwnagotchi.ui.view as view
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
from pwnagotchi.ui.components import Text
from pwnagotchi import plugins
from PIL import ImageOps, Image

class InetIcon(pwnagotchi.ui.components.Widget):
    def __init__(self, value="", position=(0, 100), color=0, png=False):
        super().__init__(position, color)
        self.value = value

    def draw(self, canvas, drawer):
        if self.value is not None:
            self.image = Image.open(self.value)
            self.image = self.image.convert('RGBA')
            self.pixels = self.image.load()
            for y in range(self.image.size[1]):
                for x in range(self.image.size[0]):
                    if self.pixels[x,y][3] < 255:    # check alpha
                        self.pixels[x,y] = (255, 255, 255, 255)
            if self.color == 255:
                self._image = ImageOps.colorize(self.image.convert('L'), black = "white", white = "black")
            else:
                self._image = self.image
            self.image = self._image.convert('1')
            canvas.paste(self.image, self.xy)   

class InternetConnectionPlugin(plugins.Plugin):
    __author__ = 'neonlightning'
    __version__ = '1.0.0'
    __license__ = 'GPL3'
    __description__ = 'A plugin that displays the Internet connection status on the pwnagotchi display.'
    __name__ = 'InternetConectionPlugin'
    __help__ = """
    A plugin that displays the Internet connection status on the pwnagotchi display.
    """

    __defaults__ = {
        'enabled': False,
    }
    def __init__(self):
        self.icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "wifi.png")

    def on_loaded(self):
        logging.info("Internet Connection Plugin loaded.")

    def on_ui_setup(self, ui):
        try:
            ui.add_element('ineticon', InetIcon(value=self.icon_path, png=True)) 
        except Exception as e:
            logging.info(f"Error loading {e}")
                         
        ui.add_element('connection_status', components.LabeledValue(color=view.BLACK, label='', value='',
                                                                   position=(10, 100), label_font=fonts.Small, text_font=fonts.Small))
        if self._is_internet_available():
            ui.set('connection_status', 'Connected')
        else:
            ui.set('connection_status', 'Disconnected')

    def on_ui_update(self, ui):
        if self._is_internet_available():
            ui.set('connection_status', 'Connected')
        else:
            ui.set('connection_status', 'Disconnected')

    def on_unload(self, ui):
        with ui._lock:
            try:
                ui.remove_element('ineticon')
            except KeyError:
                pass
            try:
                ui.remove_element('connection_status')
            except KeyError:
                pass
            
    def _is_internet_available(self):
        try:
            urllib.request.urlopen('https://www.google.com', timeout=0.5)
            return True
        except urllib.request.URLError:
            return False