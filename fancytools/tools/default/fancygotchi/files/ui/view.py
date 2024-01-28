import _thread
import logging
import random
import time
import toml
from builtins import open
import os
import re
from shutil import copy
from threading import Lock

from PIL import ImageDraw, Image, ImageSequence, ImageFont
from PIL import ImageOps

import pwnagotchi
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.faces as faces
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.ui.web as web
import pwnagotchi.utils as utils
from pwnagotchi.ui.components import *
from pwnagotchi.ui.state import State
from pwnagotchi.voice import Voice

import pwnagotchi.ui.fancygotchi as fancygotchi

WHITE = 0x00
BLACK = 0xff
ROOT = None



class View(object):
    def __init__(self, config, impl, state=None):
        global ROOT

        

        self._agent = None
        self._render_cbs = []
        self._config = config
        self._canvas = None
        self._frozen = False
        self._lock = Lock()
        self._voice = Voice(lang=config['main']['lang'])
        self._implementation = impl
        self._layout = impl.layout()
        self._width = self._layout['width']
        self._height = self._layout['height']
        self._fancygotchi = fancygotchi.fancygotchi(self, [self._width, self._height], config)
        th = pwnagotchi._theme['theme']['main_elements']
        # setup faces from the theme configuration in case the user customized them
        faces.load_from_config(th['face']['faces'])
        self._state = State(state={
            'channel': LabeledValue(color=BLACK, label='CH', value='00', position=self._layout['channel'],
                                    label_font=fonts.Bold,
                                    text_font=fonts.Medium),
            'aps': LabeledValue(color=BLACK, label='APS', value='0 (00)', position=self._layout['aps'],
                                label_font=fonts.Bold,
                                text_font=fonts.Medium),

            'uptime': LabeledValue(color=BLACK, label='UP', value='00:00:00', position=self._layout['uptime'],
                                   label_font=fonts.Bold,
                                   text_font=fonts.Medium),

            'line1': Line(self._layout['line1'], color=BLACK),
            'line2': Line(self._layout['line2'], color=BLACK),

            'face': Text(value=faces.SLEEP, position=self._layout['face'], color=BLACK, font=fonts.Huge, face=True),

            'friend_face': Text(value=None, position=self._layout['friend_face'], font=fonts.Bold, color=BLACK),
            'friend_name': Text(value=None, position=self._layout['friend_name'], font=fonts.BoldSmall,
                                color=BLACK),

            'name': Text(value='%s>' % 'pwnagotchi', position=self._layout['name'], color=BLACK, font=fonts.Bold),

            'status': Text(value=self._voice.default(),
                           position=self._layout['status']['pos'],
                           color=BLACK,
                           font=self._layout['status']['font'],
                           wrap=True,
                           # the current maximum number of characters per line, assuming each character is 6 pixels wide
                           max_length=self._layout['status']['max']),

            'shakes': LabeledValue(label='PWND ', value='0 (00)', color=BLACK,
                                   position=self._layout['shakes'], label_font=fonts.Bold,
                                   text_font=fonts.Medium),
            'mode': Text(value='AUTO', position=self._layout['mode'],
                         font=fonts.Bold, color=BLACK),
        })

        if state:
            for key, value in state.items():
                self._state.set(key, value)

        plugins.on('ui_setup', self)

        if config['ui']['fps'] > 0.0:
            _thread.start_new_thread(self._refresh_handler, ())
            self._ignore_changes = ()
        else:
            logging.warning("ui.fps is 0, the display will only update for major changes")
            self._ignore_changes = ('uptime', 'name')

        ROOT = self




    def set_agent(self, agent):
        self._agent = agent

    def has_element(self, key):
        self._state.has_element(key)

    def add_element(self, key, elem):
        self._state.add_element(key, elem)

    def remove_element(self, key):
        self._state.remove_element(key)

    def width(self):
        return self._width

    def height(self):
        return self._height

    def on_state_change(self, key, cb):
        self._state.add_listener(key, cb)

    def on_render(self, cb):
        if cb not in self._render_cbs:
            self._render_cbs.append(cb)

    def _refresh_handler(self):
        #self._fancygotchi.test()
        delay = 1.0 / self._config['ui']['fps']
        th_opt = pwnagotchi._theme['theme']['options']
        while True:
            try:
                name = self._state.get('name')
                if hasattr(pwnagotchi, 'fancy_cursor'):
                    if th_opt['cursor'] in name:
                        name = pwnagotchi.fancy_name + '>' + pwnagotchi.fancy_cursor
                        th_opt['cursor'] = pwnagotchi.fancy_cursor
                self.set('name', name.rstrip(th_opt['cursor']).strip() if th_opt['cursor'] in name else (name + th_opt['cursor']))
                self.update()

                for val in self._state.items():
                    if len(self._state.get_attr(val[0], 'colors')) != 0:
                        
                        i = self._state.get_attr(val[0], 'icolor')

                        color_list = self._state.get_attr(val[0], 'colors')
                        self._state.set_attr(val[0], 'color', color_list[i])
                        i += 1
                        if i > len(color_list)-1:
                            self._state.set_attr(val[0], 'icolor', 0)
                        else:
                            self._state.set_attr(val[0], 'icolor', i)

            except Exception as e:
                logging.warning("non fatal error while updating view: %s" % e)
                logging.warning(traceback.format_exc())
            time.sleep(delay)

    def set(self, key, value):
        self._state.set(key, value)

    def get(self, key):
        return self._state.get(key)

    def on_starting(self):
        self.set('status', self._voice.on_starting() + ("\n(v%s)" % pwnagotchi.__version__))
        self.set('face', faces.AWAKE)
        self.update()

    def on_ai_ready(self):
        self.set('mode', '  AI')
        self.set('face', faces.HAPPY)
        self.set('status', self._voice.on_ai_ready())
        self.update()

    def on_manual_mode(self, last_session):
        self.set('mode', 'MANU')
        self.set('face', faces.SAD if (last_session.epochs > 3 and last_session.handshakes == 0) else faces.HAPPY)
        self.set('status', self._voice.on_last_session_data(last_session))
        self.set('epoch', "%04d" % last_session.epochs)
        self.set('uptime', last_session.duration)
        self.set('channel', '-')
        self.set('aps', "%d" % last_session.associated)
        self.set('shakes', '%d (%s)' % (last_session.handshakes, \
                                        utils.total_unique_handshakes(self._config['bettercap']['handshakes'])))
        self.set_closest_peer(last_session.last_peer, last_session.peers)
        self.update()

    def is_normal(self):
        return self._state.get('face') not in (
            faces.INTENSE,
            faces.COOL,
            faces.BORED,
            faces.HAPPY,
            faces.EXCITED,
            faces.MOTIVATED,
            faces.DEMOTIVATED,
            faces.SMART,
            faces.SAD,
            faces.LONELY)

    def on_keys_generation(self):
        self.set('face', faces.AWAKE)
        self.set('status', self._voice.on_keys_generation())
        self.update()

    def on_normal(self):
        self.set('face', faces.AWAKE)
        self.set('status', self._voice.on_normal())
        self.update()

    def set_closest_peer(self, peer, num_total):
        if peer is None:
            self.set('friend_face', None)
            self.set('friend_name', None)
        else:
            # ref. https://www.metageek.com/training/resources/understanding-rssi-2.html
            if peer.rssi >= -67:
                num_bars = 4
            elif peer.rssi >= -70:
                num_bars = 3
            elif peer.rssi >= -80:
                num_bars = 2
            else:
                num_bars = 1

            name = '▌' * num_bars
            name += '│' * (4 - num_bars)
            name += ' %s %d (%d)' % (peer.name(), peer.pwnd_run(), peer.pwnd_total())

            if num_total > 1:
                if num_total > 9000:
                    name += ' of over 9000'
                else:
                    name += ' of %d' % num_total

            self.set('friend_face', peer.face())
            self.set('friend_name', name)
        self.update()

    def on_new_peer(self, peer):
        face = ''
        # first time they met, neutral mood
        if peer.first_encounter():
            face = random.choice((faces.AWAKE, faces.COOL))
        # a good friend, positive expression
        elif peer.is_good_friend(self._config):
            face = random.choice((faces.MOTIVATED, faces.FRIEND, faces.HAPPY))
        # normal friend, neutral-positive
        else:
            face = random.choice((faces.EXCITED, faces.HAPPY, faces.SMART))

        self.set('face', face)
        self.set('status', self._voice.on_new_peer(peer))
        self.update()
        time.sleep(3)

    def on_lost_peer(self, peer):
        self.set('face', faces.LONELY)
        self.set('status', self._voice.on_lost_peer(peer))
        self.update()

    def on_free_channel(self, channel):
        self.set('face', faces.SMART)
        self.set('status', self._voice.on_free_channel(channel))
        self.update()

    def on_reading_logs(self, lines_so_far=0):
        self.set('face', faces.SMART)
        self.set('status', self._voice.on_reading_logs(lines_so_far))
        self.update()

    def wait(self, secs, sleeping=True):
        was_normal = self.is_normal()
        part = secs/10.0

        for step in range(0, 10):
            # if we weren't in a normal state before going
            # to sleep, keep that face and status on for
            # a while, otherwise the sleep animation will
            # always override any minor state change before it
            if was_normal or step > 5:
                if sleeping:
                    if secs > 1:
                        self.set('face', faces.SLEEP)
                        self.set('status', self._voice.on_napping(int(secs)))

                    else:
                        self.set('face', faces.SLEEP2)
                        self.set('status', self._voice.on_awakening())
                else:
                    self.set('status', self._voice.on_waiting(int(secs)))

                    good_mood = self._agent.in_good_mood()
                    if step % 2 == 0:
                        self.set('face', faces.LOOK_R_HAPPY if good_mood else faces.LOOK_R)
                    else:
                        self.set('face', faces.LOOK_L_HAPPY if good_mood else faces.LOOK_L)

            time.sleep(part)
            secs -= part

        self.on_normal()

    def on_shutdown(self):
        self.set('face', faces.SLEEP)
        self.set('status', self._voice.on_shutdown())
        self.update(force=True)
        self._frozen = True

    def on_bored(self):
        self.set('face', faces.BORED)
        self.set('status', self._voice.on_bored())
        self.update()

    def on_sad(self):
        self.set('face', faces.SAD)
        self.set('status', self._voice.on_sad())
        self.update()

    def on_angry(self):
        self.set('face', faces.ANGRY)
        self.set('status', self._voice.on_angry())
        self.update()

    def on_motivated(self, reward):
        self.set('face', faces.MOTIVATED)
        self.set('status', self._voice.on_motivated(reward))
        self.update()

    def on_demotivated(self, reward):
        self.set('face', faces.DEMOTIVATED)
        self.set('status', self._voice.on_demotivated(reward))
        self.update()

    def on_excited(self):
        self.set('face', faces.EXCITED)
        self.set('status', self._voice.on_excited())
        self.update()

    def on_assoc(self, ap):
        self.set('face', faces.INTENSE)
        self.set('status', self._voice.on_assoc(ap))
        self.update()

    def on_deauth(self, sta):
        self.set('face', faces.COOL)
        self.set('status', self._voice.on_deauth(sta))
        self.update()

    def on_miss(self, who):
        self.set('face', faces.SAD)
        self.set('status', self._voice.on_miss(who))
        self.update()

    def on_grateful(self):
        self.set('face', faces.GRATEFUL)
        self.set('status', self._voice.on_grateful())
        self.update()

    def on_lonely(self):
        self.set('face', faces.LONELY)
        self.set('status', self._voice.on_lonely())
        self.update()

    def on_handshakes(self, new_shakes):
        self.set('face', faces.HAPPY)
        self.set('status', self._voice.on_handshakes(new_shakes))
        self.update()

    def on_unread_messages(self, count, total):
        self.set('face', faces.EXCITED)
        self.set('status', self._voice.on_unread_messages(count, total))
        self.update()
        time.sleep(5.0)

    def on_uploading(self, to):
        self.set('face', random.choice((faces.UPLOAD, faces.UPLOAD1, faces.UPLOAD2)))
        self.set('status', self._voice.on_uploading(to))
        self.update(force=True)

    def on_rebooting(self):
        self.set('face', faces.BROKEN)
        self.set('status', self._voice.on_rebooting())
        self.update()

    def on_custom(self, text):
        self.set('face', faces.DEBUG)
        self.set('status', self._voice.custom(text))
        self.update()

    def update(self, force=False, new_data={}):
        th_opt = pwnagotchi._theme['theme']['options']
        try:
            self._config['fancygotchi']['rotation']
        except:
            self._config['fancygotchi']['rotation'] = 0
        rot = self._config['fancygotchi']['rotation']

        for key, val in new_data.items():
            #logging.info('key: %s; val: %s' % (str(key), str(val)))
            self.set(key, val)

        with self._lock:
            if self._frozen:
                return

            state = self._state
            changes = state.changes(ignore=self._ignore_changes)
            if force or len(changes):
                if rot == 0 or rot == 180:
                    size = [self._width, self._height]
                    if th_opt['main_text_color'] == '':
                        self._canvas = Image.new('RGB', size, 'white')
                    else:
                        self._canvas = Image.new('1', size, 'white')
                elif rot == 90 or rot == 270:
                    size = [self._height, self._width] 
                    if th_opt['main_text_color'] == '':
                        self._canvas = Image.new('RGB', size, 'white')
                    else:
                        self._canvas = Image.new('1', size, 'white')

                #drawer = ImageDraw.Draw(self._canvas)
                drawer = ImageDraw.Draw(self._canvas)

                plugins.on('ui_update', self)

                #pwnagotchi.fancy_change = True
                if pwnagotchi._fancy_change == True:
                    #logging.warning(self)
                    self._fancygotchi.fancy_change()
                    #self._fancygotchi.fancy_change()
                    #if self._boot == 0:
                    pwnagotchi._fancy_change = False
                    #else:
                    #    self._boot = 0

                    
                copy_state = list(state.items())#way to avoid [WARNING] non fatal error while updating view: dictionary changed size during iteration
                for key, lv in copy_state:
                    lv.draw(self._canvas, drawer)

                #-------------------------------------------------------------------------
                # checked- Adding a foreground image option to hide the screen
                #
                # adding option for icons, icon (monochrome) or sprite
                #-------------------------------------------------------------------------

                if th_opt['main_text_color'] != '':
                    #imgtext = ImageOps.colorize(imgtext.convert('L'), black = color, white = 'white')
                    color = th_opt['main_text_color']
                    if color == 'white' : color = (254, 254, 254, 255)
                    if color != 'black':
                        self._canvas = ImageOps.colorize(self._canvas.convert('L'), black = color, white = 'white')
                    self._canvas = self._canvas.convert('RGB')


                self._canvas = self._canvas.convert('RGB')
                datas = self._canvas.getdata()
                newData_web = []
                newData_disp = []
                self._web = None
                self._disp = None
                iweb = None
                idisp = None
                # if not stealth mode enabled...*********************************************************
                if not th_opt['stealth_mode']:
                    # option colorized background
                    if th_opt['bg_color'] != '':
                        iweb = Image.new('RGBA', size, th_opt['bg_color'])
                        if th_opt['color_web']  == '2':
                            iweb = iweb.convert('RGBA')
                        elif th_opt['color_web'] != '2':
                            iweb = iweb.convert('RGBA')

                        idisp = Image.new('RGBA', size, th_opt['bg_color'])
                        if th_opt['color_display']  == '2':
                            idisp = idisp.convert('RGBA')
                        elif th_opt['color_display'] != '2':
                            idisp = idisp.convert('RGBA')
                            
                    
                    # option for animated background
                    if th_opt['bg_anim_image'] !='':
                        #logging.warning(str(self._i) +'/'+str(len(self._frames)))
                        #logging.warning(th_opt['anim_web'])
                        if self._fancygotchi._i > len(self._fancygotchi._frames):
                            self._fancygotchi._i = 0
                        if th_opt['anim_web']:
                            if isinstance(iweb, Image.Image):
                                temp_iweb = iweb.copy()
                                temp_iweb.paste(self._fancygotchi._frames[self._fancygotchi._i].convert('RGBA'))
                                iweb = temp_iweb
                            else: 
                                iweb = self._fancygotchi._frames[self._fancygotchi._i].convert('RGBA')
                        else:
                            if isinstance(iweb, Image.Image):
                                temp_iweb = iweb.copy()
                                if not self._fancygotchi._frames == []:
                                    temp_iweb.paste(self._fancygotchi._frames[0].convert('RGBA'))
                                iweb = temp_iweb
                            else: 
                                if not self._fancygotchi._frames == []:
                                    iweb = self._fancygotchi._frames[0].convert('RGBA')
                        if th_opt['anim_display']:
                            if isinstance(idisp, Image.Image):
                                temp_idisp = idisp.copy()
                                temp_idisp.paste(self._fancygotchi._frames[self._fancygotchi._i].convert('RGBA'))
                                idisp = temp_idisp
                            else: 
                                idisp = self._fancygotchi._frames[self._fancygotchi._i].convert('RGBA')
                        else:
                            if isinstance(idisp, Image.Image):
                                temp_idisp = idisp.copy()
                                if not self._fancygotchi._frames == []:
                                    temp_idisp.paste(self._fancygotchi._frames[0].convert('RGBA'))
                                idisp = temp_idisp
                            else: 
                                idisp = self._fancygotchi._frames[0].convert('RGBA')
                        if self._fancygotchi._i >= len(self._fancygotchi._frames)-1:
                            self._fancygotchi._i = 0
                    
                    
                    # option for background image
                    if th_opt['bg_image'] !='':
                        if isinstance(iweb, Image.Image):
                            temp_iweb = iweb.copy()
                            if not self._fancygotchi._bg == None:
                                temp_iweb.paste(self._fancygotchi._bg, (0,0), self._fancygotchi._bg)
                            iweb = temp_iweb
                        else: 
                            iweb = self._fancygotchi._bg.copy()
                        if isinstance(idisp, Image.Image): 
                            temp_idisp = idisp.copy()
                            if not self._fancygotchi._bg == None:
                                temp_idisp.paste(self._fancygotchi._bg, (0,0), self._fancygotchi._bg)
                            idisp = temp_idisp
                        else: 
                            idisp = self._fancygotchi._bg.copy()
                    

                    #------------------------------------------------------------------------------------------
                    for item in datas:

                        if item[0] == 255 and item[1] == 255 and item[2] == 255:
                            # white to transparent
                            newData_web.append((255, 255, 255, 0))
                            newData_disp.append((255, 255, 255, 0))

                        else:
                            if th_opt['color_web']  == '2':
                                if th_opt['color_text'] == 'white':
                                    newData_web.append((255, 255, 255, 255))
                                elif th_opt['color_text'] == 'black':
                                    newData_web.append((0, 0, 0, 255))
                                elif th_opt['color_text'] == 'auto':
                                    color_sum = item[0] + item[1] + item[2]
                                    if color_sum < 500:
                                        # color is dark
                                        newData_web.append((0, 0, 0, 255))
                                    else:
                                        # color is pale
                                        newData_web.append((255, 255, 255, 255))
                            else:
                                newData_web.append(item) #version for color mode
                            if th_opt['color_display']  == '2':
                                if th_opt['color_text'] == 'white':
                                    newData_disp.append((255, 255, 255, 255))
                                elif th_opt['color_text'] == 'black':
                                    newData_disp.append((0, 0, 0, 255))
                                elif th_opt['color_text'] == 'auto':
                                    color_sum = item[0] + item[1] + item[2]
                                    if color_sum < 500:
                                        # color is dark
                                        newData_disp.append((0, 0, 0, 255))
                                    else:
                                        # color is pale
                                        newData_disp.append((255, 255, 255, 255))
                            else:
                                newData_disp.append(item) #version for color mode

                    #------------------------------------------------------------------------------------------

                    # maybe adding an option to make certain components
                    # under the foreground layer and other above it for
                    # a stelth mode
                    #
                    # adding the canvas layer
                    
                    if isinstance(iweb, Image.Image):
                        temp_data_iweb = Image.new('RGBA', size, (255, 255, 255, 0))
                        temp_data_iweb.putdata(newData_web)
                        iweb.paste(temp_data_iweb, (0,0), temp_data_iweb)

                    else:
                        temp_data_iweb = Image.new('RGBA', size, (255, 255, 255, 0))
                        temp_data_iweb.putdata(newData_web)
                        iweb = temp_data_iweb
                        
                    if isinstance(idisp, Image.Image):
                        temp_data_idisp = Image.new('RGBA', size, (255, 255, 255, 0))
                        temp_data_idisp.putdata(newData_disp)
                        idisp.paste(temp_data_idisp, (0,0), temp_data_idisp)

                    else:
                        temp_data_idisp = Image.new('RGBA', size, (255, 255, 255, 0))
                        temp_data_idisp.putdata(newData_disp)
                        idisp = temp_data_idisp
                    
                # end of the not stealth mode **************************************************************

                    #if stealth mode, don't activate it on the web UI
                    if th_opt['fg_image'] != '':
                        if isinstance(iweb, Image.Image):
                            temp_iweb = iweb.copy()
                            temp_iweb.paste(self._fancygotchi._fg, (0,0), self._fancygotchi._fg)
                            iweb = temp_iweb
                        else:
                            iweb = self._fancygotchi._fg
                        if isinstance(idisp, Image.Image):
                            temp_idisp = idisp.copy()
                            temp_idisp.paste(self._fancygotchi._fg, (0,0), self._fancygotchi._fg)
                            idisp = temp_idisp
                        else:
                            idisp = self._fancygotchi._fg
                else:
                    logging.info('[FANCYGOTCHI] stealth Mode')
                
                if th_opt['color_web']  == '2':
                    self._web = iweb.convert('1')
                else:
                    self._web = iweb.convert('RGB')
                if th_opt['color_display']  == '2':
                    self._disp = idisp.convert('1')
                else:
                    self._disp = idisp.convert('RGB')
                
                if rot == 0 or rot == 180:
                    img = self._disp
                if rot == 90 or rot == 270:
                    img = self._disp.rotate(90, expand=True)

                if rot == 180 or rot == 270:
                    img = img.rotate(180)
                for cb in self._render_cbs:
                    cb(img)

                web.update_frame(self._web)

                if hasattr(self._fancygotchi, '_frames') and (th_opt['anim_web'] or th_opt['anim_display']):
                    self._fancygotchi._i += 1


                self._state.reset()