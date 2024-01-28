import logging
import os
import toml
import time

from PIL import ImageDraw, Image, ImageSequence, ImageFont
from PIL import ImageOps

from shutil import copy
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.ui.faces as faces

import pwnagotchi

def text_to_rgb(text, tfont, color, width, height):
    try:
        th_opt = pwnagotchi._theme['theme']['options']
        if color == 'white' : color = (254, 254, 254, 255)
        if color == 255 : color = 'black'
        w,h = tfont.getsize(text)
        nb_lines = text.count('\n') + 1
        h = (h + 1) * nb_lines
        if nb_lines > 1:
            lines = text.split('\n')
            max_char = 0
            tot_char = 0
            for line in lines:
                tot_char = tot_char + len(line)
                char_line = len(line)
                if char_line > max_char: max_char = char_line
            w = int(w / (tot_char / max_char))
        imgtext = Image.new('1', (int(w), int(h)), 0xff)
        dt = ImageDraw.Draw(imgtext)
        dt.text((0,0), text, font=tfont, fill=0x00)
        if color == 0: color = 'black'
        imgtext = ImageOps.colorize(imgtext.convert('L'), black = color, white = 'white')
        imgtext = imgtext.convert('RGB')
        return imgtext
    except Exception as e:
        logging.warning("Error:", str(e))
        return None

def adjust_image(image_path, zoom, mask=False):
    try:
        # Open the image
        image = Image.open(image_path)
        image = image.convert('RGBA') 
        #image.save('/home/pi/original.png')
        # Get the original width and height
        original_width, original_height = image.size
        # Calculate the new dimensions based on the zoom factor
        new_width = int(original_width * zoom)
        new_height = int(original_height * zoom)
        # Resize the image while maintaining the aspect ratio
        adjusted_image = image.resize((new_width, new_height))
        if mask:
            image = adjusted_image.convert('RGBA') 
            width, height = image.size
            pixels = image.getdata()
            new_pixels = []
            for pixel in pixels:
                r, g, b, a = pixel
                # If pixel is not fully transparent (alpha is not 0), convert it to black
                #if a > 50:
                if a > 150:
                    new_pixel = (0, 0, 0, 255)
                else:
                    new_pixel = (0, 0, 0, 0)
                new_pixels.append(new_pixel)
            # Create a new image with the modified pixel data
            new_img = Image.new("RGBA", image.size)
            new_img.putdata(new_pixels)
            adjusted_image = new_img
        return adjusted_image
    except Exception as e:
        logging.warning("Error:", str(e))
        return None

class fancygotchi(object):
    __name__ = 'Fancygotchi'
    __author__ = '@V0rT3x https://github.com/V0r-T3x'
    __version__ = '2023.09.1'
    __license__ = 'GPL3'
    __description__ = 'A theme manager for the Pwnagotchi [cannot be disabled, need to be uninstalled from inside the plugin]'

    def __init__(self, view, res, config):
        #logging.warning('Fancygotchi object loaded')
        self._view = view
        self._i = 0
        self._frames = []
        self._i = 0
        self._config = config
        self._res = res
        self._theme = []
        self._fancy_theme = ''
        self._fancy_theme_disp = ''
        self._fancy_change = True
        self._bg = None
        self.theme_selector(self._res, self._config, True)

    def theme_selector(self, size, config, boot=False):
        self.size = size
        #logging.info("Loading theme...")
        pwny_path = os.path.dirname(pwnagotchi.__file__)
        display_path = '%s/ui/hw' % (pwny_path)
        #logging.warning(display_path)
        #logging.warning(config['fancygotchi']['theme'])
        try: 
            config['fancygotchi']['theme']
        except:
            config['fancygotchi'] = {'theme':''}

        if not config['fancygotchi']['theme'] == '':
            th_select = str(config['fancygotchi']['theme'])
        else:
            th_select = '.default'
        resolution = '%sx%s' % (str(self.size[0]), str(self.size[1]))
        #logging.warning(resolution)
        custom_path = config['main']['custom_plugins']
        if not custom_path == '':
            if custom_path[-1] == '/':
                custom_path = custom_path[:-1]
        if th_select == '.default' or not os.path.exists('%s/themes/%s' % (custom_path, th_select)):
            th_path = '%s/ui/themes/' % (pwny_path)
            if not os.path.exists('%s/themes/%s' % (custom_path, th_select)):
                logging.warning("Theme not found in custom path, using default")
        else:
            th_path = '%s/themes/%s/' % (custom_path, th_select)
        th_path_disp = '%s%s/' % (th_path, resolution)
        #logging.warning(th_path)
        rot = config['ui']['display']['rotation']
        if rot == 0 or rot == 180 :
            #logging.info('%sconfig-h.toml' % (th_path_disp))
            config_ori = '%sconfig-h.toml' % (th_path_disp)
        elif rot == 90 or rot == 270:
            #logging.info('%sconfig-v.toml' % (th_path_disp))
            config_ori = '%sconfig-v.toml' % (th_path_disp)
        with open(config_ori, 'r') as f:
            setattr(pwnagotchi, '_theme', toml.load(f))
            #self._theme = toml.load(f)
            setattr(pwnagotchi, '_fancy_theme', th_path)
            setattr(pwnagotchi, '_fancy_theme_disp', th_path_disp)
            setattr(pwnagotchi, 'fancy_name', config['main']['name'])
            #logging.warning(boot)
            if boot:
                setattr(pwnagotchi, '_fancy_change', True)
        #logging.warning('here')
        #logging.warning(pwnagotchi._theme)

        # copying the style.css of the selected theme
        src_css = '%sstyle.css' % (th_path)
        dst_css = '%s/web/static/css/style.css' % (os.path.dirname(os.path.realpath(__file__)))
        #logging.info('[FANCYGOTCHI] linking theme css: '+src_css +' ~~mod~~> '+ dst_css)
        copy(src_css, dst_css)

        # changing the symlink for the img folder of the slected theme
        src_img = '%simg' % (th_path)
        dst_img = '%s/web/static' % (os.path.dirname(os.path.realpath(__file__)))
        #logging.info('[FANCYGOTCHI] linking theme image folder: '+src_img +' ~~mod~~> '+ dst_img)
        # removing old link
        os.system('rm %s/img' % (dst_img))
        # creating new link
        os.system('ln -s %s %s' % (src_img, dst_img))

    def fancy_change(self, partial=False, fancy_dict=[]):
        #logging.warning('Fancygotchi fancychange')
        i = 0
        out = False
        while not out:
            global Bold, BoldSmall, Medium, Huge, BoldBig, Small, FONT_NAME
            rot = self._config['fancygotchi']['rotation']
            th_opt = pwnagotchi._theme['theme']['options']
            actual_th = self._config['fancygotchi']['theme']
        
            #logging.warning(i)
            if not partial:
                # loading pwnagotchi config.toml
                with open('/etc/pwnagotchi/config.toml', 'r') as f:
                    f_toml = toml.load(f)
                    try:
                        self._config['fancygotchi']['rotation'] = f_toml['fancygotchi']['rotation']
                    except:
                        self._config['fancygotchi']['rotation'] = 0
                rot = self._config['fancygotchi']['rotation']
                self.theme_selector(self.size, f_toml)

            else:
                logging.info('[FANCYGOTCHI] partial theme refresh: %s' % (fancy_dict))
            bga_path = '%simg/%s' % (pwnagotchi._fancy_theme, th_opt['bg_anim_image'])

            if th_opt['bg_anim_image'] != '' and os.path.exists(bga_path):
                #logging.warning('%simg/%s' % (pwnagotchi._fancy_theme, th_opt['bg_anim_image']))
                gif = Image.open(bga_path)
                self._frames = []
                for frame in ImageSequence.Iterator(gif):
                    self._frames.append(frame.convert("RGBA"))
            bg_path = '%simg/%s' % (pwnagotchi._fancy_theme, th_opt['bg_image'])
            if th_opt['bg_image'] != '' and os.path.exists(bg_path):
                self._bg = Image.open(bg_path)
                self._bg = self._bg.convert('RGBA')
            fg_path = '%simg/%s' % (pwnagotchi._fancy_theme, th_opt['fg_image'])
            if th_opt['fg_image'] != '' and os.path.exists(fg_path):
                self._fg = Image.open(fg_path)
                self._fg = self._fg.convert('RGBA')

            setattr(pwnagotchi, 'fancy_cursor', th_opt['cursor'])
            th_opt['cursor'] = th_opt['cursor']
            setattr(pwnagotchi, 'fancy_font', th_opt['cursor'])
            fonts.STATUS_FONT_NAME = th_opt['status_font']
            fonts.SIZE_OFFSET = th_opt['size_offset']
            fonts.FONT_NAME = th_opt['font']

            ft = th_opt['font_sizes']
            fonts.setup(ft[0], ft[1], ft[2], ft[3], ft[4], ft[5])

            main_elements = pwnagotchi._theme["theme"]["main_elements"]
            plugin_elements = pwnagotchi._theme["theme"]["plugin_elements"]
            components = main_elements.copy()
            components.update(plugin_elements)

            for element, values in components.items():
                for key, value in values.items():
                    if element == 'status':
                        s = True
                    else:
                        s = False
                    if key in ['label', 'label_spacing', 'label_line_spacing', 'f_awesome', 'f_awesome_size']:
                        self._view._state.set_attr(element, key, value)
                    elif key == 'position':
                        self._view._state.set_attr(element,'xy', value)
                    elif key == 'font':
                        if value == 'Small': 
                            if not s:
                                self._view._state.set_font(element, fonts.Small)
                            else:
                                self._view._state.set_font(element, fonts.status_font(fonts.Small))
                        elif value == 'Medium': 
                            if not s:
                                self._view._state.set_font(element, fonts.Medium)
                            else:
                                self._view._state.set_font(element, fonts.status_font(fonts.Medium))
                        elif value == 'BoldSmall':
                            if not s:
                                self._view._state.set_font(element, fonts.BoldSmall)
                            else:
                                self._view._state.set_font(element, fonts.status_font(fonts.BoldSmall))
                        elif value == 'Bold':
                            if not s:
                                self._view._state.set_font(element, fonts.Bold)
                            else:
                                self._view._state.set_font(element, fonts.status_font(fonts.Bold))
                        elif value == 'BoldBig':
                            if not s:
                                self._view._state.set_font(element, fonts.BoldBig)
                            else:
                                self._view._state.set_font(element, fonts.status_font(fonts.BoldBig))
                        elif value == 'Huge':
                            if not s:
                                self._view._state.set_font(element, fonts.Huge)
                            else:
                                self._view._state.set_font(element, fonts.status_font(fonts.Huge))
                    elif key == 'text_font':
                        if value == 'Small': self._view._state.set_textfont(element, fonts.Small)
                        elif value == 'Medium': self._view._state.set_textfont(element, fonts.Medium)
                        elif value == 'BoldSmall': self._view._state.set_textfont(element, fonts.BoldSmall)
                        elif value == 'Bold': self._view._state.set_textfont(element, fonts.Bold)
                        elif value == 'BoldBig': self._view._state.set_textfont(element, fonts.BoldBig)
                        elif value == 'Huge': self._view._state.set_textfont(element, fonts.Huge)
                    elif key == 'label_font':
                        if value == 'Small': self._view._state.set_labelfont(element, fonts.Small)
                        elif value == 'Medium': self._view._state.set_labelfont(element, fonts.Medium)
                        elif value == 'BoldSmall': self._view._state.set_labelfont(element, fonts.BoldSmall)
                        elif value == 'Bold': self._view._state.set_labelfont(element, fonts.Bold)
                        elif value == 'BoldBig': self._view._state.set_labelfont(element, fonts.BoldBig)
                        elif value == 'Huge': self._view._state.set_labelfont(element, fonts.Huge)
                    elif key == 'color':
                        self._view._state.set_attr(element, key, value)
                        self._view._state.set_attr(element, '%ss' % key, [])
                    elif key == 'colors':
                        self._view._state.set_attr(element, key, [])
                        if len(value) != 0:
                            #logging.warning('more than one color')
                            color_list = [self._view._state.get_attr(element, 'color')]
                            color_list.extend(value)
                            #logging.warning(color_list)
                            self._view._state.set_attr(element, key, color_list)
                        else:
                            self._view._state.set_attr(element, key, [])

                    elif key == 'icon':
                        self._view._state.set_attr(element, key, value)
                        for ckey, cvalue in components[element].items():
                            if not element == 'face':
                                if value:
                                    for val in self._view._state.items():
                                        if val[0] == element:
                                            if isinstance(val[1], pwnagotchi.ui.components.LabeledValue):
                                                #logging.warning(element+' is a labeled value')
                                                type = self._view._state.get_attr(element, 'label')
                                                t = 'label'
                                            elif isinstance(val[1], pwnagotchi.ui.components.Text):
                                                #if not 'face' in components[element].items():
                                                #logging.warning(element+' is a text')
                                                type = self._view._state.get_attr(element, 'value')
                                                t = 'value'
                                    if not components[element]['f_awesome']:
                                        #if not 'face' in components[element].items():
                                        icon_path = '%simg/%s' % (pwnagotchi.fancy_theme, type)
                                        ##self._view._state.image = Image.open(icon_path)
                                        zoom = 1
                                        for ckey, cvalue in components[element].items():
                                            if ckey == 'zoom':
                                                zoom = cvalue
                                                if not th_opt['main_text_color'] == '':
                                                    mask = True
                                                else:
                                                    mask = False
                                        self._view._state.set_attr(element, 'image',  adjust_image(icon_path, zoom, mask))#Image.open(icon_path))
                                        if th_opt['main_text_color'] != '':
                                            self.image.convert('1')
                                    else:
                                        #logging.warning(t)
                                        fa = ImageFont.truetype('font-awesome-solid.otf', components[element]['f_awesome_size'])
                                        code_point = int(components[element][t], 16)
                                        icon = chr(code_point)
                                        w,h = fa.getsize(icon)
                                        icon_img = Image.new('1', (int(w), int(h)), 0xff)
                                        dt = ImageDraw.Draw(icon_img)
                                        dt.text((0,0), icon, font=fa, fill=0x00)
                                        icon_img = icon_img.convert('RGBA')
                                        self._view._state.set_attr(element, 'image', icon_img)
                    elif key == 'faces':
                        for ckey, cvalue in components[element].items():
                            if ckey == 'icon':
                                isiconic = cvalue
                        if isiconic:
                            for ckey, cvalue in components[element].items():
                                if ckey == 'faces':
                                    th_faces = cvalue
                                if ckey == 'image_type':
                                    th_img_t = cvalue
                            faces.load_from_config(value)
                            mapping = {}
                            for face_name, face_value in th_faces.items():
                                icon_path = '%simg/%s.%s' % (pwnagotchi._fancy_theme, face_name, th_img_t)
                                icon_broken = '%simg/%s.%s' % (pwnagotchi._fancy_theme, 'broken', th_img_t)
                                zoom = 1
                                for ckey, cvalue in components[element].items():
                                    mask = False
                                    if ckey == 'zoom':
                                        zoom = cvalue
                                        if not th_opt['main_text_color'] == '':
                                            mask = True
                                        else:
                                            mask = False
                                if os.path.isfile(icon_path):
                                    face_image = adjust_image(icon_path, zoom, mask)
                                else:
                                    #logging.warning('[FANCYGOTCHI] missing the %s image' % (face_name))
                                    face_image = adjust_image(icon_broken, zoom, mask)
                                #self.mapping = {face_value: face_image}
                                mapping[face_value] = face_image
                            self._view._state.set_attr(element, 'face_map', mapping)
            i += 1
            if i == 2:
                out = True







        pwnagotchi._fancy_change = False

