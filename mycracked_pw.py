import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import qrcode
import html
import csv
import os
import io


class MyCrackedPasswords(plugins.Plugin):
    __author__ = '@silentree12th'
    __version__ = '5.1.1'
    __license__ = 'GPL3'
    __description__ = 'A plugin to grab all cracked passwords and creates wifi qrcodes and a wordlist which can be used for the quickdic plugin. It stores them in the home directory. Read with cat'

    def on_loaded(self):
        logging.info("[mycracked_pw] loaded]")
        if not os.path.exists('/home/pi/wordlists/'):
            os.makedirs('/home/pi/wordlists/')
            
        if not os.path.exists('/home/pi/qrcodes/'):
            os.makedirs('/home/pi/qrcodes/')
            
        self._update_all()
        
    def on_handshake(self, agent, filename, access_point, client_station):
        self._update_all()
        
        
    def _update_all(self):
        all_passwd=[]
        all_bssid=[]
        all_ssid=[]
        f=open('/root/handshakes/wpa-sec.cracked.potfile', 'r+', encoding='utf-8')
        try:
            for line_f in f:
                pwd_f = line_f.split(':')
                all_passwd.append(str(pwd_f[-1].rstrip('\n')))
                all_bssid.append(str(pwd_f[0]))
                all_ssid.append(str(pwd_f[-2]))
        except:
            logging.error('[mycracked_pw] encountered a problem in wpa-sec.cracked.potfile')
        f.close()
        
        h = open('/root/handshakes/onlinehashcrack.cracked', 'r+', encoding='utf-8')
        try:
            for line_h in csv.DictReader(h):
                pwd_h = str(line_h['password'])
                bssid_h = str(line_h['BSSID'])
                ssid_h = str(line_h['ESSID'])
                if pwd_h and bssid_h and ssid_h:
                    all_passwd.append(pwd_h)
                    all_bssid.append(bssid_h)
                    all_ssid.append(ssid_h)
        except:
            logging.error('[mycracked_pw] encountered a problem in onlinehashcrack.cracked')
        h.close()
        
        #save all the wifi-qrcodes
        security="WPA"
        for ssid,password in zip(all_ssid, all_passwd):
            
            filename = ssid+'-'+password+'.txt'
            filepath = '/home/pi/qrcodes/'+filename
            
            if os.path.exists(filepath):
                continue
                
            wifi_config = 'WIFI:S:'+ssid+';T:'+security+';P:'+password+';;'
            
            # Create the QR code object
            qr_code = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr_code.add_data(wifi_config)
            qr_code.make(fit=True)
            
            try:
                with open(filepath, 'w+') as file:
                    qr_code.print_ascii(out=file)
                    q = io.StringIO()
                    qr_code.print_ascii(out=q)
                    q.seek(0)
                    logging.info(filename)
                    logging.info(q.read())
            except:
                logging.error("[mycracked_pw] something went wrong generating qrcode")
            logging.info("[mycracked_pw] qrcode generated.")

                    
            # start with blank file
            open('/home/pi/wordlists/mycracked.txt', 'w+').close()
        
            #create pw list
            new_lines = sorted(set(all_passwd))
            with open('/home/pi/wordlists/mycracked.txt','w+') as g:
                for i in new_lines:
                    g.write(i+"\n")
        
            logging.info("[mycracked_pw] pw list updated")
