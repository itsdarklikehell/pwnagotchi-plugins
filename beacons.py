import time
import _thread
import logging
import base64
import pwnagotchi
import pwnagotchi.plugins as plugins
import pwnagotchi.grid as grid
import pwnagotchi.ui.faces as faces
from scapy.all import Dot11,Dot11Beacon,Dot11Elt,Dot11EltRates,RadioTap,sendp,hexdump,get_if_hwaddr
from struct import *

class Beacons(plugins.Plugin):
    __author__ = '@kripthor'
    __version__ = '0.0.2'
    __license__ = 'GPL3'
    __description__ = 'A plugin that advertises pwnagotchi state via valid WiFi beacons.'

    _iface = 'mon0'
    _wifimac = ''
    _packet_type = { 'report':1, 'info':2, 'peers':3 }
    _mode = { 'MANU':0b0000000, 'AUTO':0b01000000, '  AI':0b10000000 }
    _faces = [ faces.LOOK_R, faces.LOOK_L, faces.LOOK_R_HAPPY, faces.LOOK_L_HAPPY, faces.SLEEP, faces.SLEEP2, faces.AWAKE, faces.BORED, faces.INTENSE, faces.COOL, faces.HAPPY, faces.GRATEFUL, faces.EXCITED, faces.MOTIVATED, faces.DEMOTIVATED, faces.SMART, faces.LONELY, faces.SAD, faces.ANGRY, faces.FRIEND, faces.BROKEN, faces.DEBUG]

    _busy = False

    def __init__(self):
        logging.debug(" *beacons* plugin created")
        self._wifimac = open('/sys/class/net/'+self._iface+'/address').readline()[0:17]

    # called when the plugin is loaded
    def on_loaded(self):
        logging.warning(" *beacons* this plugin is not stealthy at all! Anyone could see the beacons when they search for WiFi networks!")
        Beacons._busy = False

    # called when there's internet connectivity
    def on_internet_available(self, agent):
        pass

    # called when the ui is updated
    def on_ui_update(self, ui):
        if Beacons._busy:
            logging.debug(" *beacons* -> ui_update busy to send " + str(time.time()) )
            return
        _thread.start_new_thread(self.exec_update, (ui,))
        #self.exec_update(ui)

    # This function bypasses the locks on the State. It's not ideal, but it was hanging too much. Need a safer way to do this.
    def get_unsafe_unsync(self, ui, key):
       return ui._state._state[key].value if key in ui._state._state else None

    def exec_update(self,ui):
        try:
            Beacons._busy = True
           #TODO parse and send peers in another beacon frame
            packedInfo = self.pack_info(self.get_unsafe_unsync(ui,'channel'),self.get_unsafe_unsync(ui,'aps'), self.get_unsafe_unsync(ui,'shakes'),pwnagotchi.uptime(),self.get_unsafe_unsync(ui,'face'),self.get_unsafe_unsync(ui,'mode'),pwnagotchi.name())
            self.broadcast_info(packedInfo,self._packet_type['report'])
        except Exception as e:
            logging.warning(" *beacons* -> exec_update exception: ")
            logging.warning(" *beacons* -> " + str(type(e)) )
            logging.warning(" *beacons* -> " + str(e) )
        Beacons._busy = False

    def pack_info(self,channel,aps,shakes,uptime,face,mode,name):
        #pack channel info into first byte
        c = 0
        try:
            c = int(str(channel))
        except:
            if str(channel) == '*' :
                c = 0b00111111
            elif str(channel) == '-' :
                c = 0b00111110
            else:
                c = 0
        #pack AP in current channel and total APs
        ac = 0
        at = 0
        pr = 0
        pt = 0
        try:
            i = aps.index(' ')
            ac = int(aps[0:i])
            at = int(aps[i+2:-1])
        except:
            ac = int(aps)

        try:
            i = shakes.index(' ')
            pr = int(shakes[0:i])
            pt = int(shakes[i+2:-1])
        except:
            pass


        up = int(uptime)
        m =  int(self._mode[mode])
        f = int(self._faces.index(face))
        cm = m + c
        #result = pack('!HHHHIHBB',ac,at,pr,pt,up,f,c,m)
        logging.debug(" *beacons* -> packing state: " + str(face) + " pwnd_run: "+ str(pr) + " pwnd_total: "+ str(pt) )
        result = pack('!B',ac & 0xff)+pack('!H',at)+pack('!H',pr)+pack('!H',pt)+pack('!I',up)+pack('!B',f)+pack('!B',cm)
        # 13 bytes full. We can add 11 more to have 24 bytes size, and base64 the result to the 32 bytes, maximum SSID len that ensures compatibility cross platform
        result += bytes(name,'utf-8')[0:11]
        return base64.b64encode(result)


    def broadcast_info(self,info_packet,packet_type):
#        logging.warning(" *beacons* -> sending packets " + str(time.time()) )
        SSID = info_packet
        iface = self._iface
        #android has some kind of mac filtering for vendors, not all spoofed macs work.
#        sender = "de:ad:be:ef:de:ad"
        sender = self._wifimac[0:3] + "13:37:" + self._wifimac[9:] 
        dot11 = Dot11(type=0, subtype=8, addr1='ff:ff:ff:ff:ff:ff',addr2=sender, addr3=sender)
        beacon = Dot11Beacon()
        essid = Dot11Elt(ID='SSID',info=SSID, len=len(SSID))
        rate_channel = b'\x01\x08\x82\x84\x8b\x96\x0c\x12\x18\x24\x03\x01'+pack('B',packet_type)+b'\x32\x04\x30\x48\x60\x6c'
        frame = RadioTap()/dot11/beacon/essid/rate_channel
        sendp(frame, iface=iface, inter=0.100, count=30)


    # called when a new peer is detected
    def on_peer_detected(self, agent, peer):
        pass

    # called when a known peer is lost
    def on_peer_lost(self, agent, peer):
        pass
