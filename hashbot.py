#! /usr/bin/python3

__author__ = "v0yager"
__license__ = "GPL3"
__version__ = "1.0.0"
__description__ = """
                This bot will return the hashes obtained using discohash
                for a specified number of access points as a txt file.
                Message the bot with !dumphash [NUMBER].
                """

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# 1. Create a bot in the Discord developer portal
# 2. Grant it the required permissions (message_content)
# 3. Obtain a token and the channel ID
# 4. Add these to a .env file containted in the same directory

load_dotenv()
TOKEN = os.getenv('example')
GUILD = os.getenv('example')
CHANNEL = os.getenv('example')


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.command(name="dumphash")
async def on_message(ctx, num_hashes=int(1000)):
    try:
        with open('hashes.22000', 'w') as f:
            channel = bot.get_channel(int(CHANNEL)) 
            message = channel.history(limit=int(num_hashes)) 
            async for i in message: 
                hash_dict = i.embeds[0].to_dict() 
                hash = hash_dict['fields'][0]['value']
                f.write(hash[1:-1])
        f.close()
        with open('hashes.22000', 'r') as f:
            await ctx.send(file=discord.File(f, 'hashcat.22000.txt'))
            f.close()
    except KeyboardInterrupt:
        await bot.close()
        exit(0)

bot.run(TOKEN)
