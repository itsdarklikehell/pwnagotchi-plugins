import os
import requests
from pwnagotchi import plugins


class CustomVoicePlugin(plugins.Plugin):
    __author__ = "MaliosDark"
    __version__ = "1.0.0"
    __license__ = "MIT"
    __description__ = "Plugin to download and replace voice.py with a custom version"

    def on_loaded(self):
        print("Custom Voice Plugin loaded.")

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
            print("Custom voice.py installed successfully.")
        except Exception as e:
            print(f"Error installing custom voice.py: {e}")

    def on_unload(self):
        print("Custom Voice Plugin unloaded.")


# Instanciar el plugin
custom_voice_plugin = CustomVoicePlugin()
