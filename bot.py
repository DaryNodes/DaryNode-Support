import disnake
import logging
from disnake.ext import commands
import os
import json


config = json.load(open('config.json'))
bot = commands.Bot(command_prefix=config["prefix"])
# Load cogs
bot.load_extension("cogs.ping")


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # Process command
    await bot.process_commands(message)
    # If not command then autorespond
    await handle_response(message)


async def handle_response(message: disnake.Message):
    """ Handle auto responses """
    for file in os.listdir('./responses'):
        file_json = json.load(open('./responses/' + file))
        for trigger in file_json['triggers']:
            if trigger.lower() in message.content.lower():
                return await message.reply(file_json['response'])

# Sets up Logging
logger = logging.getLogger('disnake')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='disnake.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot.run(config["token"])
