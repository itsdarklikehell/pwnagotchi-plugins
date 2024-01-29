# THIS IS A TEST. TO LOAD THE NEW UI USING JUST A PLUGIN.
# THIS PLUGIN IS BEING TESTED
# DO NOT USE UNTIL TESTS ARE CONFIRMED AND RESULTS ARE AVAILABLE
# I DO INSIST!!
# JUST WAIT A BIT
# INF YOU WANT TO TEST IT. YO NEED TO HAVE INSTALLED VERSION 1.5.5 PWNAGOTCHI
# THIS IS BASSICALY A AUTOMATION OF THIS TUTORIAL https://github.com/roodriiigooo/PWNAGOTCHI-CUSTOM-FACES-MOD

# IF THIS MESSAGE IS STILL SHOWING HERE IS BECAUSE THE PLUGIN DOES NOT WORK YET.
# IT ACTIVATES BUT DOES NOT SHOW THE IMAGES, ONLY THE ROUTE TO THEM
# ALSO DOES MAKE A CHANGE IN THE CONFIG.TOM WHERE DUPLICATES THE UI FACES.


import subprocess
import sys
import os
import shutil
import logging

from pwnagotchi.ui.components import Widget, Text
import pwnagotchi.plugins as plugins


class EgirlThemePlugin(plugins.Plugin):
    # Rutas de archivos
    CONFIG_FILE = '/etc/pwnagotchi/config.toml'
    COMPONENTS_FILE = '/usr/local/lib/python3.11/dist-packages/pwnagotchi/ui/components.py'
    VIEW_FILE = '/usr/local/lib/python3.11/dist-packages/pwnagotchi/ui/view.py'
    BACKUP_COMPONENTS_FILE = '/files-backup/components.py'
    BACKUP_VIEW_FILE = '/files-backup/view.py'
    CUSTOM_FACES_DIRECTORY = '/custom-faces/egirl-pwnagotchi'

    __author__ = 'MaliosDark'
    __version__ = '1.2.2'
    __name__ = "Egirl Theme"
    __license__ = 'GPL3'
    __description__ = 'Plugin to activate/deactivate the egirl-pwnagotchi theme'

    def __init__(self):
        super().__init__()

        # Variable to track whether the theme is enabled or disabled
        self.theme_enabled = False

    def install_dependencies(self):
        logging.info("Installing dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests'])

    def on_loaded(self):
        if not self.theme_enabled:
            self.install_dependencies()
            logging.info("Egirl Theme loaded")

            pwnagotchi_directory = '/custom-faces'
            theme_repo = 'https://github.com/PersephoneKarnstein/egirl-pwnagotchi/archive/master.zip'
            custom_faces_directory = self.download_and_extract(
                theme_repo, pwnagotchi_directory)
            self.update_config(custom_faces_directory)
            self.restart_pwnagotchi()
            subprocess.run(['reboot'])

            # Marcar que el tema está habilitado para evitar volver a cargarlo
            self.theme_enabled = True
        else:
            logging.info("Egirl Theme already loaded. Skipping installation.")

    def download_and_extract(self, url, destination):
        logging.info("Downloading and extracting theme files...")

        os.system(f'wget {url} -O /tmp/egirl-pwnagotchi-master.zip')
        os.system(f'unzip /tmp/egirl-pwnagotchi-master.zip -d {destination}')

        faces_directory = os.path.join(
            destination, 'egirl-pwnagotchi-master/faces')
        os.makedirs(self.CUSTOM_FACES_DIRECTORY, exist_ok=True)

        for file_name in os.listdir(faces_directory):
            source_path = os.path.join(faces_directory, file_name)
            destination_path = os.path.join(
                self.CUSTOM_FACES_DIRECTORY, file_name)
            shutil.move(source_path, destination_path)

        logging.info("Theme files extracted and moved successfully.")
        return self.CUSTOM_FACES_DIRECTORY

    def update_config(self, custom_faces_directory):
        logging.info("Updating Pwnagotchi configuration...")

        face_mapping = {
            'look_r': "( ⚆‿⚆)",
            'look_l': "(☉‿☉ )",
            'look_r_happy': "( ◔‿◔)",
            'look_l_happy': "(◕‿◕ )",
            'sleep': "(⇀‿‿↼)",
            'sleep2': "(≖‿‿≖)",
            'awake': "(◕‿‿◕)",
            'bored': "(-__-)",
            'intense': "(°▃▃°)",
            'cool': "(⌐■_■)",
            'happy': "(•‿‿•)",
            'excited': "(ᵔ◡◡ᵔ)",
            'grateful': "(^‿‿^)",
            'motivated': "(☼‿‿☼)",
            'demotivated': "(≖__≖)",
            'smart': "(✜‿‿✜)",
            'lonely': "(ب__ب)",
            'sad': "(╥☁╥ )",
            'angry': "( ¬_¬')",
            'friend': "(♥‿‿♥)",
            'broken': "(☓‿‿☓)",
            'debug': "(#__#)",
            'upload': "(⇀‸↼)",
            'upload1': "(⇀_⇀)",
            'upload2': "(↼_↼)"
        }

        with open(self.CONFIG_FILE, 'r') as f:
            config_lines = f.readlines()

        updated_lines = []
        updated = False

        for line in config_lines:
            for face_name, new_path in face_mapping.items():
                if f'ui.faces.{face_name}' in line:
                    updated_lines.append(
                        f'ui.faces.{face_name} = "{custom_faces_directory}/{face_name.upper()}.png"\n')
                    updated = True
                    break
            else:
                updated_lines.append(line)

        if updated:
            with open(self.CONFIG_FILE, 'w') as f:
                f.writelines(updated_lines)

            logging.info("Pwnagotchi configuration updated successfully.")
        else:
            logging.info("No updates needed in Pwnagotchi configuration.")

    def modify_paths_in_components(self, source_file, destination_file, custom_faces_directory):
        logging.info("Modifying paths in components.py...")

        # Backup components.py
        shutil.copy(source_file, self.BACKUP_COMPONENTS_FILE)

        # Modify components.py
        with open(source_file, 'r') as f:
            content = f.read()

        modified_content = content.replace(
            'class Text(Widget):',
            'class Text(Widget):\n    def __init__(self, value="", position=(0, 0), font=None, color=0, wrap=False, max_length=0, png=False):\n        super().__init__(position, color)\n        self.value = value\n        self.font = font\n        self.wrap = wrap\n        self.max_length = max_length\n        self.wrapper = TextWrapper(width=self.max_length, replace_whitespace=False) if wrap else None\n        self.png = png\n        self.image = None  # Agregamos esta línea para almacenar la imagen\n\n    def draw(self, canvas, drawer):\n        if self.value is not None and not self.png:\n            if self.wrap:\n                text = \'\\n\'.join(self.wrapper.wrap(self.value))\n            else:\n                text = self.value\n            drawer.text(self.xy, text, font=self.font, fill=self.color)\n        elif self.value is not None and self.png:\n            if self.image is None:\n                self.image = Image.open(self.value)\n                self.image = self.image.convert(\'RGBA\')\n                self.pixels = self.image.load()\n                for y in range(self.image.size[1]):\n                    for x in range(self.image.size[0]):\n                        if self.pixels[x, y][3] < 255:    # check alpha\n                            self.pixels[x, y] = (255, 255, 255, 255)\n                if self.color == 255:\n                    self._image = ImageOps.colorize(self.image.convert(\'L\'), black="white", white="black")\n                else:\n                    self._image = self.image\n                self.image = self._image.convert(\'1\')\n            canvas.paste(self.image, self.xy)'
        )

        with open(destination_file, 'w') as f:
            f.write(modified_content)

        logging.info("Modified components.py successfully.")

    def modify_paths_in_view(self, source_file, destination_file, custom_faces_directory):
        logging.info("Modifying paths in view.py...")

        # Backup view.py
        shutil.copy(source_file, self.BACKUP_VIEW_FILE)

        # Modify view.py
        with open(source_file, 'r') as f:
            content = f.read()

        modified_content = content.replace(
            "'face': Text(value=faces.SLEEP, position=self._layout['face'], color=BLACK, font=fonts.Huge),",
            "'face': Text(value=faces.SLEEP, position=(config['ui']['faces']['position_x'], config['ui']['faces']['position_y']), color=BLACK, font=fonts.Huge, png=config['ui']['faces']['png']),"
        )

        with open(destination_file, 'w') as f:
            f.write(modified_content)

        logging.info("Modified view.py successfully.")

    def move_images_to_custom_faces(self, src_directory, dest_directory):
        logging.info("Moving images to custom-faces directory...")

        # Ensure destination directory exists
        os.makedirs(dest_directory, exist_ok=True)

        # Move images
        for file_name in os.listdir(src_directory):
            source_path = os.path.join(src_directory, file_name)
            destination_path = os.path.join(dest_directory, file_name)
            shutil.move(source_path, destination_path)

        logging.info("Images moved to custom-faces directory successfully.")

    def modify_paths(self):
        # Move images to custom-faces directory
        self.move_images_to_custom_faces(
            '/custom-faces/egirl-pwnagotchi-master/faces', self.CUSTOM_FACES_DIRECTORY)

        # Modify paths in components.py
        self.modify_paths_in_components(
            self.COMPONENTS_FILE, self.COMPONENTS_FILE, self.CUSTOM_FACES_DIRECTORY)

        # Modify paths in view.py
        self.modify_paths_in_view(
            self.VIEW_FILE, self.VIEW_FILE, self.CUSTOM_FACES_DIRECTORY)

    def handle_revert_button(self):
        self.uninstall()
        logging.info("Changes reverted successfully.")

    def uninstall(self):
        logging.info("Uninstalling Egirl Theme...")

        # Revertir cambios en config.toml
        with open(self.CONFIG_FILE, 'r') as f:
            config_lines = f.readlines()

        updated_lines = [
            line for line in config_lines if 'ui.faces.' not in line]

        with open(self.CONFIG_FILE, 'w') as f:
            f.writelines(updated_lines)

        # Revertir cambios en components.py
        shutil.copy(self.BACKUP_COMPONENTS_FILE, self.COMPONENTS_FILE)

        # Revertir cambios en view.py
        shutil.copy(self.BACKUP_VIEW_FILE, self.VIEW_FILE)

        logging.info("Egirl Theme uninstalled successfully.")
