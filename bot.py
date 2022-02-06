import disnake
from disnake.ext import commands
import json
import views
import functions


# load configs
config = json.load(open('config.json'))

bot = commands.Bot(command_prefix=config["prefix"])

# Load cogs
bot.load_extension("cogs.ping")
bot.load_extension("cogs.ticketing")
bot.load_extension("cogs.pterodactyl")


@bot.event
async def on_ready():
    await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name="out for errors!", assets={"large_text": "DaryNodes"}), status="online")
    print(f'Bot logged in as {bot.user}')
    bot.db = await functions.setup_database()


@bot.event
async def on_message(message):
    ticket_document = await bot.db['tickets'].find_one(
        {"channel_id": str(message.channel.id)})

    if ticket_document is not None:
        # the message was in a ticket channel
        # log = ticket_document['message_log']
        log_inp = {
            "author": message.author.name,
            "time": message.created_at,
            "content": message.content,
            "avatar": message.author.avatar.url
        }
        await bot.db['tickets'].update_one({'channel_id': str(message.channel.id)}, {'$addToSet': {'message_log': log_inp}})

    if message.author == bot.user:
        return

    # Process commands
    await bot.process_commands(message)

    # If not command then handle autorespond
    await functions.handle_response(message)


@bot.event
async def on_button_click(inter: disnake.MessageInteraction):
    if inter.data.custom_id == 'close_ticket':
        emb = disnake.Embed(
            title="Are you sure?",
            color=disnake.Color.red(),
            description="Are you sure you want to close this ticket? This action cannot be undone."
        )
        emb.set_footer(text="Expires in 30 seconds")
        await inter.send(embed=emb, ephemeral=True, view=views.confirm_button(bot.db))


# Sets up Logging
functions.setup_logging()

bot.run(config["token"])
