#! /usr/bin/python3
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv


class hashbot(plugins.Plugin):
    __author__ = "(edited by: itsdarklikehell bauke.molenaar@gmail.com), v0yager"
    __license__ = "GPL3"
    __version__ = "1.0.0"
    __description__ = "This bot will return the hashes obtained using discohash for a specified number of access points as a txt file. Message the bot with !dumphash [NUMBER]."
    __name__ = "hashbot"
    __help__ = "This bot will return the hashes obtained using discohash for a specified number of access points as a txt file. Message the bot with !dumphash [NUMBER]."
    __dependencies__ = {
        "apt": ["none"],
        "pip": ["scapy"],
    }
    __defaults__ = {
        "enabled": False,
    }

    # 1. Create a bot in the Discord developer portal
    # 2. Grant it the required permissions (message_content)
    # 3. Obtain a token and the channel ID
    # 4. Add these to a .env file containted in the same directory
    def __init__(self):
        self.ready = False
        logging.debug(f"[{self.__class__.__name__}] plugin init")
        self.title = ""
        TOKEN = os.getenv("example")
        GUILD = os.getenv("example")
        CHANNEL = os.getenv("example")
        bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
        @bot.command(name="dumphash")

    def on_loaded(self):
        data_path = "/root/hashes.22000"
        self.load_data(data_path)
        logging.info(f"[{self.__class__.__name__}] plugin loaded")

    def on_unload(self, ui):
        with ui._lock:
            logging.info(f"[{self.__class__.__name__}] plugin unloaded")

    def on_webhook(self, path, request):
        logging.info(f"[{self.__class__.__name__}] webhook pressed")

    def load_data(self, data_path):
        if os.path.exists(data_path):

            async def on_message(ctx, num_hashes=int(1000)):
                try:
                    with open(data_path) as f:
                        channel = bot.get_channel(int(CHANNEL))
                        message = channel.history(limit=int(num_hashes))
                        async for i in message:
                            hash_dict = i.embeds[0].to_dict()
                            hash = hash_dict["fields"][0]["value"]
                            f.write(hash[1:-1])
                    f.close()
                    with open(data_path) as f:
                        await ctx.send(file=discord.File(f, "hashcat.22000.txt"))
                    f.close()
                except KeyboardInterrupt:
                    await bot.close()
