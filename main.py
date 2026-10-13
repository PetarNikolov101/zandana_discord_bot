import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
import asyncio

load_dotenv()
token = os.getenv("DISCORDTOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

async def main():
    async with bot:
        await bot.load_extension("cogs.dice_roll")
        await bot.load_extension("cogs.welcome")
        await bot.load_extension("cogs.find")
        await bot.start(token)

asyncio.run(main())