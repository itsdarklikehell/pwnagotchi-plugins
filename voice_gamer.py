import os
import requests
from pwnagotchi import plugins


class CustomVoicePlugin(plugins.Plugin):
    __GitHub__ = ""
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), MaliosDark"
    __version__ = "1.0.0"
    __license__ = "MIT"
    __description__ = "Plugin to download and replace voice.py with a custom version"

    def on_loaded(self):
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    def on_config_changed(self, config):
        if "custom_voice_url" in config["main"]:
            custom_voice_url = config["main"]["custom_voice_url"]
            self.download_and_replace_voice(custom_voice_url)

    def download_and_replace_voice(self, custom_voice_url):
        try:
            response = requests.get(custom_voice_url)
            response.raise_for_status()
            custom_voice_content = response.text

            # Guardar el contenido en un archivo temporal
            temp_file_path = "/tmp/custom_voice.py"
            with open(temp_file_path, "w") as temp_file:
                temp_file.write(custom_voice_content)

            # Reemplazar voice.py con el archivo personalizado
            os.system(
                f"sudo cp {temp_file_path} /usr/local/lib/python3.11/dist-packages/pwnagotchi/voice.py"
            )
            logging.info("Custom voice.py installed successfully.")
        except Exception as e:
            logging.info(f"Error installing custom voice.py: {e}")

    def on_unload(self):
        logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")


# Instanciar el plugin
custom_voice_plugin = CustomVoicePlugin()
