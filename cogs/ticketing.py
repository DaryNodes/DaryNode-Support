from ast import Str
from datetime import datetime
from time import sleep
import disnake
from disnake.ext import commands
import json


class Ticketing(commands.Cog):
    """This will be for a ping command."""

    def __init__(self, bot: commands.Bot):
        print("LOADED Ticketing")
        self.bot = bot

    @commands.command(name="raiseticket")
    async def _rt(self, ctx: commands.Context, category):
        """Raise a ticket"""
        if category == 'gen' or category == 'general':
            ticket_no = await self.bot.db.tickets.count_documents({"category": "general"}) + 1
            info_collection = await self.bot.db['general_info'].find_one({"guild_id": str(ctx.guild.id)})
            category_id = info_collection['tickets']['gen_category']
            category = await ctx.guild.fetch_channel(category_id)
            channel = await ctx.guild.create_text_channel(name=f"{ticket_no}-{ctx.author.name}", category=category)
            await self.bot.db.tickets.insert_one({
                "category": "general",
                "ticket_no": int(ticket_no),
                "guild_id": str(ctx.guild.id),
                "channel_id": str(channel.id),
                "user_id": str(ctx.author.id) + "#" + str(ctx.author.discriminator),
                "user_name": str(ctx.author.name),
                "raised_at": datetime.utcnow(),
                "status": "open",
                "message_log": []
            })
            help_role_id = info_collection['tickets']['gen_category_role']
            role = ctx.guild.get_role(int(help_role_id))
            await channel.set_permissions(ctx.author, read_messages=True, send_messages=True, read_message_history=True)
            await channel.set_permissions(role, read_messages=True, send_messages=True, read_message_history=True)
            await channel.send(
                f"{ctx.author.mention} Hello! Please answer the following questions so our support team can help you.")
            await self.init_ticket(ctx, channel, "general")
        elif category == 'paid':
            ticket_no = await self.bot.db.tickets.count_documents({"category": "paid"}) + 1
            info_collection = await self.bot.db['general_info'].find_one({"guild_id": str(ctx.guild.id)})
            category_id = info_collection['tickets']['paid_category']
            category = await ctx.guild.fetch_channel(category_id)
            channel = await ctx.guild.create_text_channel(name=f"{ticket_no}-{ctx.author.name}", category=category)
            await self.bot.db.tickets.insert_one({
                "category": "paid",
                "ticket_no": int(ticket_no),
                "guild_id": str(ctx.guild.id),
                "channel_id": str(channel.id),
                "user_id": str(ctx.author.id) + "#" + str(ctx.author.discriminator),
                "user_name": str(ctx.author.name),
                "raised_at": datetime.utcnow(),
                "status": "open",
                "message_log": []
            })
            help_role_id = info_collection['tickets']['paid_category_role']
            role = ctx.guild.get_role(int(help_role_id))
            await channel.set_permissions(ctx.author, read_messages=True, send_messages=True, read_message_history=True)
            await channel.set_permissions(role, read_messages=True, send_messages=True, read_message_history=True)
            await channel.send(
                f"{ctx.author.mention} Hello! Please answer the following questions so our support team can help you.")
            await self.init_ticket(ctx, channel, "paid")
        elif category == 'panel':
            ticket_no = await self.bot.db.tickets.count_documents({"category": "panel"}) + 1
            info_collection = await self.bot.db['general_info'].find_one({"guild_id": str(ctx.guild.id)})
            category_id = info_collection['tickets']['panel_category']
            category = await ctx.guild.fetch_channel(category_id)
            channel = await ctx.guild.create_text_channel(name=f"{ticket_no}-{ctx.author.name}", category=category)
            await self.bot.db.tickets.insert_one({
                "category": "panel",
                "ticket_no": int(ticket_no),
                "guild_id": str(ctx.guild.id),
                "channel_id": str(channel.id),
                "user_id": str(ctx.author.id) + "#" + str(ctx.author.discriminator),
                "user_name": str(ctx.author.name),
                "raised_at": datetime.utcnow(),
                "status": "open",
                "message_log": []
            })
            help_role_id = info_collection['tickets']['panel_category_role']
            role = ctx.guild.get_role(int(help_role_id))
            await channel.set_permissions(ctx.author, read_messages=True, send_messages=True, read_message_history=True)
            await channel.set_permissions(role, read_messages=True, send_messages=True, read_message_history=True)
            await channel.send(
                f"{ctx.author.mention} Hello! Please answer the following questions so our support team can help you.")
            await self.init_ticket(ctx, channel, "panel")
        else:
            return await ctx.reply(
                "Please choose a vaild category :gun:\n\n **Available Choices:** \n`general`\n`paid`\n`panel`")
        msg = await ctx.reply(f"Ticket raised!")
        await ctx.message.delete(delay=5)
        await msg.delete(delay=5)

    async def init_ticket(self, ctx: commands.Context, channel: disnake.TextChannel, category: str):
        # TODO: Initiate ticket and get the info
        pass

    @commands.command(name="closeticket")
    async def _closeticket(self, ctx: commands.context):
        ticket_collection = self.bot.db['tickets']
        ticket_doc = await ticket_collection.find_one(
            {"channel_id": str(ctx.channel.id)})
        if ticket_doc is None:
            return await ctx.reply(f"This channel is not a ticket channel.")
        if ticket_doc['status'] == 'closed':
            return await ctx.reply(f"This channel is already closed.")
        ticket_collection.update_one({"channel_id": str(ctx.channel.id)}, {
                                     "$set": {"status": "closed"}})
        await ctx.channel.send(f"This ticket has been closed by {ctx.author.mention}.")
        return await ctx.channel.delete(reason=f"Closed by {ctx.author.name}.")


def setup(bot: commands.Bot):
    bot.add_cog(Ticketing(bot))
