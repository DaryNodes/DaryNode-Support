from ast import Lambda
from datetime import datetime
from time import sleep
import asyncio
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
        await ctx.message.delete(delay=5)

    async def init_ticket(self, ctx: commands.Context, channel: disnake.TextChannel, category: str):
        """Initialize a ticket"""
        msg = await channel.send("Please describe your issue in less than 100 words. The request shall timeout in 180 seconds.")
        try:
            ans = await self.bot.wait_for('message', check=lambda m: m.author ==
                                          ctx.author and m.channel == channel, timeout=180)
        except asyncio.TimeoutError:
            emb = disnake.Embed(
                title=f"Ticket Number: {channel.name.split('-')[0]}",
                description="None provided",
                color=disnake.Color.green()
            )
            emb.set_author(name=ctx.author.name,
                           icon_url=ctx.author.avatar_url)
        else:
            emb = disnake.Embed(
                title=f"Ticket Number: {channel.name.split('-')[0]}",
                description=ans.content,
                color=disnake.Color.green()
            )
        emb.set_footer(
            text=f"Please wait for the support team to respond.")
        emb.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        emb.add_field(name="Category", value=category)
        close_button = self.close_button()
        await channel.purge(limit=3)
        await channel.send(embed=emb, view=close_button)

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

    class close_button(disnake.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @disnake.ui.button(
            label="Close",
            style=disnake.ButtonStyle.danger,
            custom_id="close_ticket",
            emoji="🔒"
        )
        async def close(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
            pass

    @commands.command(name="getlog")
    async def _get_ticket_log(self, ctx: commands.Context, ticket_number: str, category: str):
        if ticket_number is None:
            return await ctx.reply("Please provide a ticket number.")
        if category is None:
            return await ctx.reply("Please provide a category.")
        ticket_collection = self.bot.db['tickets']
        doc = await ticket_collection.find_one({"ticket_no": int(ticket_number), "category": category})
        if not doc:
            return await ctx.reply(f"No ticket found with number {ticket_number} in category {category}.")
        final_reply = []
        for msg in doc['message_log']:
            final_reply.append(
                f"```\n{msg['author']}:\n{msg['content']}\nat: {str(msg['time'])}\n```")
        for reply in final_reply:
            await ctx.send(reply)

    @commands.command(name="createpanel")
    async def _create_panel(self, ctx: commands.Context):
        channel = ctx.channel
        ctx.reply("Reply with the title of the new panel. Times out in 120 seconds")
        self.bot.wait_for(
            "on_message", lambda message: message.user == ctx.author, timeout=120)


def setup(bot: commands.Bot):
    bot.add_cog(Ticketing(bot))