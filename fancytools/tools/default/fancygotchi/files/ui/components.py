import logging
import pwnagotchi
import pwnagotchi.ui.fancygotchi as fancygotchi
from PIL import Image, ImageDraw, ImageOps, ImageFont
from textwrap import TextWrapper
import sys
import os




class Widget(object):
    def __init__(self, xy, color=0):
        self.xy = xy
        self.color = color
        self.icolor = 0
        self.colors = []

    def draw(self, canvas, drawer):
        raise Exception("not implemented")



class Bitmap(Widget):
    def __init__(self, path, xy, color=0):
        super().__init__(xy, color)
        self.image = Image.open(path)

    def draw(self, canvas, drawer):
        canvas.paste(self.image, self.xy)


class Line(Widget):
    def __init__(self, xy, color=0, width=1):
        super().__init__(xy, color)
        self.width = width

    def draw(self, canvas, drawer):
        drawer.line(self.xy, fill=self.color, width=self.width)


class Rect(Widget):
    def draw(self, canvas, drawer):
        drawer.rectangle(self.xy, outline=self.color)


class FilledRect(Widget):
    def draw(self, canvas, drawer):
        drawer.rectangle(self.xy, fill=self.color)


class Text(Widget):
#    def __init__(self, value="", position=(0, 0), font=None, color=0, wrap=False, max_length=0):
    def __init__(self, value="", position=(0, 0), font=None, color=0, wrap=False, max_length=0, icon=False, f_awesome=False, f_awesome_size=0, face=False, zoom=1):

        super().__init__(position, color)
        th_opt = pwnagotchi._theme['theme']['options']
        #logging.warning(color)

        self.value = value
        self.font = font
        self.wrap = wrap
        self.max_length = max_length
        self.wrapper = TextWrapper(width=self.max_length, replace_whitespace=False) if wrap else None
        self.icon = icon
        self.image = None
        self.f_awesome = f_awesome
        self.f_awesome_size = f_awesome_size
        self.face = face
        self.zoom = zoom
        th = pwnagotchi._theme['theme']['main_elements']
        self.face_map = {}
        self.friend_map = {}
        th_faces = th['face']['faces']
        th_img_t = th['face']['image_type']
        if not th_opt['main_text_color'] == '':
            self.mask = True
        else:
            self.mask = False

    def get_font(self):
        return self.font

    def draw(self, canvas, drawer):
        th_opt = pwnagotchi._theme['theme']['options']
        if self.value is not None:
            if not self.icon:
                if self.wrap:
                    text = '\n'.join(self.wrapper.wrap(self.value))
                else:
                    text = self.value
                #logging.warning(str(self.color))
                width, height = canvas.size
                if th_opt['main_text_color'] == '':
                    imgtext = fancygotchi.text_to_rgb(text, self.font, self.color, width, height)
                    #logging.warning(str(self.value) + ' = ' + str(imgtext))
                    #logging.info("canvas: %s" % canvas.mode)
                    #logging.info("self.xy: %s" % self.xy)
                    if len(self.xy) >= 3:
                        x = self.xy[0]
                        y = self.xy[1]
                    else:
                        x, y = self.xy
                    
                    if imgtext != None:
                        w, h = imgtext.size
                        canvas.paste(imgtext, (int(x), int(y), int(x) + w, int(y) + h))
                else:
                    #logging.warning(text)
                    drawer.text(self.xy, text, font=self.font, fill=0x00)
                    #drawer.text(self.xy, text, self.font, font=self.font, fill=self.color)
            else:
                if not self.f_awesome:
                    if not self.face:
                        canvas.paste(self.image, self.xy, self.image)
                    else:
                        img = self.face_map[self.value]
                        #img.save('/home/pi/actual.png')
                        canvas.paste(img, self.xy, img)
                        #canvas.paste(self.image, self.xy, self.image)
                else:
                    if self.color == 'white' : self.color = (254, 254, 254, 255)
                    if th_opt['main_text_color'] == '':
                        icon_img = ImageOps.colorize(self.image.convert('L'), black = self.color, white = 'white')
                        icon_img = icon_img.convert('RGBA')
                        canvas.paste(icon_img, self.xy, icon_img)
                    else:
                        canvas.paste(self.image, pos_label, self.image)

class LabeledValue(Widget):
    def __init__(self, label, value="", position=(0, 0), label_font=None, text_font=None, color=0, label_spacing=9, icon=False, label_line_spacing=0, f_awesome=False, f_awesome_size=0, zoom=1):
        th_opt = pwnagotchi._theme['theme']['options']
        label_spacing = th_opt['label_spacing']
        super().__init__(position, color)
        self.label = label
        self.value = value
        self.label_font = label_font
        self.text_font = text_font
        self.label_spacing = label_spacing
        self.label_line_spacing = label_line_spacing
        self.icon = icon
        self.image = None
        self.zoom = zoom
        self.f_awesome = f_awesome
        self.f_awesome_size = f_awesome_size
        if not th_opt['main_text_color'] == '':
            self.mask = True
        else:
            self.mask = False
        if icon:
            if not self.f_awesome:
                icon_path = '%simg/%s' % (pwnagotchi._fancy_theme, label)
                self.image =  adjust_image(icon_path, self.zoom, self.mask)#Image.open(icon_path)
                if th_opt['main_text_color'] != '':
                    self.image.convert('1')
            else:
                fa = ImageFont.truetype('font-awesome-solid.otf', self.f_awesome_size)
                code_point = int(self.label, 16)
                icon = code_point
                w,h = fa.getsize(icon)
                icon_img = Image.new('1', (int(w), int(h)), 0xff)
                dt = ImageDraw.Draw(icon_img)
                dt.text((0,0), icon, font=fa, fill=0x00)
                icon_img = icon_img.convert('RGBA')
                self.image = icon_img

    def draw(self, canvas, drawer):
        th_opt = pwnagotchi._theme['theme']['options']
        width, height = canvas.size
        pos_label = [int(self.xy[0]), int(self.xy[1]) + self.label_line_spacing]
        pos_value = (pos_label[0] + self.label_spacing + 5 * len(self.label), pos_label[1] - self.label_line_spacing)
        if self.label is None:
            if th_opt['main_text_color'] == '':
                imgtext = fancygotchi.text_to_rgb(self.value, self.label_font, self.color, width, height)
                canvas.paste(imgtext, self.xy)
            else:
                drawer.text(self.xy, self.value, font=self.label_font, fill=0x00)
                #drawer.text(self.xy, self.value, font=self.label_font, fill=self.color)
        else:
            if not self.icon:

                #logging.info('%s   --   %s' % (str(pos_label), str(pos_value)))
                if th_opt['main_text_color'] == '':
                    imgtext = fancygotchi.text_to_rgb(self.label, self.label_font, self.color, width, height)
                    canvas.paste(imgtext, pos_label)
                    imgtext = fancygotchi.text_to_rgb(self.value, self.text_font, self.color, width, height)
                    canvas.paste(imgtext, pos_value)
                else:
                    drawer.text(pos_label, self.label, font=self.label_font, fill=0x00)
                    drawer.text(pos_value, self.value, font=self.text_font, fill=0x00)
            else:
                #logging.warning(self.f_awesome)
                if not self.f_awesome:
                    canvas.paste(self.image, pos_label, self.image)
                else:
                    if self.color == 'white' : self.color = (254, 254, 254, 255)
                    #logging.warning(self.color)
                    if th_opt['main_text_color'] == '':
                        icon_img = ImageOps.colorize(self.image.convert('L'), black = self.color, white = 'white')
                        icon_img = icon_img.convert('RGBA')
                        canvas.paste(icon_img, pos_label, icon_img)
                    else:
                        canvas.paste(self.image, pos_label, self.image)

                if th_opt['main_text_color'] == '':
                    imgtext = fancygotchi.text_to_rgb(self.value, self.text_font, self.color, width, height)
                    canvas.paste(imgtext, pos_value)
                else:
                    drawer.text(pos_value, self.value, font=self.text_font, fill=0x00)