import logging
import os
import json
import disnake
import motor.motor_asyncio
import asyncio
from disnake.ext import commands
import views

config = json.load(open('config.json'))


async def handle_response(message: disnake.Message):
    """ Handle auto responses """
    for file in os.listdir('./responses'):
        file_json = json.load(open('./responses/' + file))
        for trigger in file_json['triggers']:
            if trigger.lower() in message.content.lower():
                return await message.reply(file_json['response'])
    return


def setup_logging():
    """Sets up the logger"""
    logger = logging.getLogger('disnake')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(
        filename='disnake.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


async def setup_database():
    """ Setup mongo database """
    print("Setting Up MongoDB!")
    connection = motor.motor_asyncio.AsyncIOMotorClient(
        config["mongoDB_connection_url"])
    print("MongoDB Connection Successful!")
    try:
        db = connection[config["mongoDB_database_name"]]
        print("MongoDB Checking database")
        if db['genral_info'] is None:
            print("MongoDB Database is not setup- EXITING")
            exit(1)
        print("MongoDB Database Loaded!")
    except Exception as e:
        print(f"MongoDB Failed to load database: {e}, EXIT.")
        exit(1)
    return db


async def init_ticket(ctx: commands.Context, channel: disnake.TextChannel, category: str, bot: disnake.Client):
    """Initialize a ticket"""
    msg = await channel.send("Please describe your issue in less than 100 words. The request shall timeout in 180 seconds.")
    try:
        ans = await bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == channel, timeout=180)
    except asyncio.TimeoutError:
        emb = disnake.Embed(
            title=f"Ticket Number: {channel.name.split('-')[0]}",
            description="None provided",
            color=disnake.Color.green()
        )
        emb.set_footer(
            text=f"Please wait for the support team to respond. If you already own a server on our paid plan, please type in {config['prefix']}serverinfo <support code> to help us resolve your issue faster!")
        emb.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    else:
        emb = disnake.Embed(
            title=f"Ticket Number: {channel.name.split('-')[0]}",
            description=ans.content,
            color=disnake.Color.green()
        )
    emb.set_footer(
        text=f"Please wait for the support team to respond. If you already own a server on our paid plan, please type in {config['prefix']}serverinfo <support code> to help us resolve your issue faster!")
    emb.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    emb.add_field(name="Category", value=category)
    if category == 'paid':
        # TODO: CHECK IF THEY HAVE THE PAID USER ROLE! IF SO PING THE SUPPORT TEAM!
        text = f"Priority Support"
    else:
        text = "If you want priority support, you can get a paid server!"
    await channel.purge(limit=3)
    await channel.send(content=text, embed=emb, view=views.close_button())
