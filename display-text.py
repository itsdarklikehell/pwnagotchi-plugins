import logging
import pwnagotchi.ui.components as components
import pwnagotchi.ui.view as view
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi


class displaytext(plugins.Plugin):
    __author__ = "SgtStroopwafel, adi1708 made by chatGPT"
    __version__ = "1.0.0"
    __license__ = "GPL3"
    __description__ = "A plugin that displays text on the waveshare144lcd screen."
    __name__ = "displaytext"
    __help__ = "A plugin that displays text on the waveshare144lcd screen."
    __dependencies__ = {"pip": ["scapy"]}
    __defaults__ = {
        "enabled": false,
    }

    def on_loaded(self):
        logging.info("My Plugin loaded.")

    def on_ui_setup(self, ui):
        # add a LabeledValue element to the UI with the given label and value
        # the position and font can also be specified
        ui.add_element(
            "my_element",
            components.Text(
                color=view.BLACK,
                value="Hello World!",
                position=(0, 50),
                font=fonts.Small,
            ),
        )

    def on_ui_update(self, ui):
        # update the value of the 'my_element' element with the desired text
        ui.set("my_element", "Hello World!")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")
