# spotify_now_playing.py

import pwnagotchi
import threading
from pwnagotchi import plugins
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging

class SpotifyNowPlaying(plugins.Plugin):
    __author__ = 'vanshksingh'
    __version__ = '1.0.0'
    __license__ = 'GPL3'

    def on_loaded(self):
        self.last_song = None
        self.song_lock = threading.Lock()

        # Load Spotify API credentials from config.toml
        config = pwnagotchi.Config()
        spotify_config = config['spotify_now_playing']
        
        client_id = spotify_config.get('client_id', 'YOUR_CLIENT_ID')
        client_secret = spotify_config.get('client_secret', 'YOUR_CLIENT_SECRET')
        redirect_uri = spotify_config.get('redirect_uri', 'YOUR_REDIRECT_URI')

        # Set up Spotify API credentials
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                                            client_secret=client_secret,
                                                            redirect_uri=redirect_uri,
                                                            scope='user-read-currently-playing'))
        self.logger = logging.getLogger('spotify_now_playing')

    def on_unload(self, ui):
        pass

    def on_ui_update(self, ui):
        with self.song_lock:
            current_song = self.get_current_song()
            if current_song and current_song != self.last_song:
                ui.display.draw_text((0, 0), f"Spotify: {current_song}")
                self.last_song = current_song

    def get_current_song(self):
        try:
            current_track = self.sp.current_playback()
            if current_track is not None and 'item' in current_track:
                return current_track['item']['name']
        except spotipy.SpotifyException as spe:
            # Handle Spotify API exceptions
            self.logger.error(f"Spotify API error: {spe}")
        except Exception as e:
            # Handle other exceptions
            self.logger.error(f"Error fetching current song: {e}")
        return "No Song Playing"

# Instantiate the plugin
spotify_now_playing = SpotifyNowPlaying()
