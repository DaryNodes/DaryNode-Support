import datetime
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


@bot.event
async def on_dropdown(interaction: disnake.MessageInteraction):
    await interaction.response.defer(ephemeral=True)
    if interaction.data.custom_id == 'raiseticket':
        ticket_no = await bot.db.tickets.count_documents({"category": f"{interaction.data.values[0]}"}) + 1
        info_collection = await bot.db['general_info'].find_one({"guild_id": str(interaction.guild.id)})
        cat = None
        rol = None
        if interaction.data.values[0] == 'general':
            cat = "gen_category"
            rol = "gen_category_role"
        elif interaction.data.values[0] == 'paid':
            cat = "paid_category"
            rol = "paid_category_role"
        elif interaction.data.values[0] == 'panel':
            cat = "panel_category"
            rol = "panel_category_role"
        else:
            interaction.send("LOL IT BROKE!", ephemeral=True)
        category_id = info_collection['tickets'][cat]
        category = await interaction.guild.fetch_channel(category_id)
        channel = await interaction.guild.create_text_channel(name=f"{ticket_no}-{interaction.author.name}", category=category)
        await bot.db.tickets.insert_one({
            "category": f"{interaction.data.values[0]}",
            "ticket_no": int(ticket_no),
            "guild_id": str(interaction.guild.id),
            "channel_id": str(channel.id),
            "user_id": str(interaction.author.id) + "#" + str(interaction.author.discriminator),
            "user_name": str(interaction.author.name),
            "raised_at": datetime.datetime.utcnow(),
            "status": "open",
            "message_log": []
        })
        help_role_id = info_collection['tickets'][rol]
        role = interaction.guild.get_role(int(help_role_id))
        await channel.set_permissions(interaction.author, read_messages=True, send_messages=True, read_message_history=True)
        await channel.set_permissions(role, read_messages=True, send_messages=True, read_message_history=True)
        await interaction.send(f"ticket raised! Answer the question at {channel.mention}", ephemeral=True)
        await channel.send(
            f"{interaction.author.mention} Hello! Please answer the following questions so our support team can help you.")
        await functions.init_ticket(interaction, channel, f"{interaction.data.values[0]}", bot)


# Sets up Logging
functions.setup_logging()

bot.run(config["token"])
