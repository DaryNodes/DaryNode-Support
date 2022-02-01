import disnake
import logging
from disnake.ext import commands
import os
import json
import motor.motor_asyncio


config = json.load(open('config.json'))
bot = commands.Bot(command_prefix=config["prefix"])
# Load cogs
bot.load_extension("cogs.ping")
bot.load_extension("cogs.ticketing")


@bot.event
async def on_ready():
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name="out for errors!", assets={"large_text": "DaryNodes"}), status="online")
    print(f'We have logged in as {bot.user}')
    bot.db = await setup_database()


@bot.event
async def on_message(message):
    ticket_document = await bot.db['tickets'].find_one(
        {"channel_id": str(message.channel.id)})
    if ticket_document is not None:
        log = ticket_document['message_log']
        log_inp = {
            "author": message.author.name,
            "time": message.created_at,
            "content": message.content,
            "avatar": message.author.avatar.url
        }
        log.append(log_inp)
        await bot.db['tickets'].update_one({'channel_id': str(message.channel.id)}, {'$set': {'message_log': log}})
    if message.author == bot.user:
        return
    # Process command
    await bot.process_commands(message)
    # If not command then autorespond
    await handle_response(message)


@bot.event
async def on_button_click(inter: disnake.MessageInteraction):
    if inter.data.custom_id == 'close_ticket':
        emb = disnake.Embed(
            title="Are you sure?",
            color=disnake.Color.red(),
            description="Are you sure you want to close this ticket? This action cannot be undone."
        )
        emb.set_footer(text="Expires in 30 seconds")
        await inter.send(embed=emb, ephemeral=True, view=confirm_button())


class confirm_button(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=30)

    @disnake.ui.button(
        label="Confirm",
        style=disnake.ButtonStyle.danger,
        custom_id="confirm_close",
        emoji="⚠️"
    )
    async def close(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer(ephemeral=True)
        ticket_collection = bot.db['tickets']
        ticket_doc = await ticket_collection.find_one(
            {"channel_id": str(interaction.channel.id)})
        if ticket_doc is None:
            return await interaction.send(f"This channel is not a ticket channel.")
        if ticket_doc['status'] == 'closed':
            return await interaction.send(f"This channel is already closed.")
        ticket_collection.update_one({"channel_id": str(interaction.channel.id)}, {
                                     "$set": {"status": "closed"}})
        await interaction.send(f"This ticket has been closed by {interaction.author.mention}.")
        return await interaction.channel.delete(reason=f"Closed by {interaction.author.name}.")

    @disnake.ui.button(
        label="Cancel",
        style=disnake.ButtonStyle.gray,
        custom_id="cancel_close",
    )
    async def cancel_close(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        return await interaction.send("OK! Cancelled", ephemeral=True)


async def handle_response(message: disnake.Message):
    """ Handle auto responses """
    for file in os.listdir('./responses'):
        file_json = json.load(open('./responses/' + file))
        for trigger in file_json['triggers']:
            if trigger.lower() in message.content.lower():
                await message.channel.trigger_typing()
                return await message.reply(file_json['response'])


async def setup_database():
    """ Setup mongo database """
    print("Setting Up MongoDB!")
    connection = motor.motor_asyncio.AsyncIOMotorClient(
        config["mongoDB_connection_url"])
    print("Connection Successful!")
    try:
        db = connection[config["mongoDB_database_name"]]
        print("Checking database")
        if db['genral_info'] is None:
            print("Database is not setup.")
            exit(1)
        print("Database Loaded!")
    except Exception as e:
        print(f"Failed to load database: {e}")
        exit(1)
    return db

# Sets up Logging
logger = logging.getLogger('disnake')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='disnake.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot.run(config["token"])
