from unicodedata import name
from disnake.ext import commands
import requests
import json
import disnake

config = json.load(open('config.json'))


class pterodactyl_Commands(commands.Cog):
    """Category for pterodactyl commands."""

    def __init__(self, bot: commands.Bot):
        print("Loaded pterodactyl Category")
        self.bot = bot

    @commands.command(name="serverinfo")
    async def _serverinfo(self, ctx: commands.Context, server_id="null"):
        if server_id == 'null':
            return await ctx.reply("Please enter the support code.")
        url = f"{config['pterodactyl_url']}/api/client/servers/{server_id}"
        headers = {
            "Authorization": f"Bearer {config['pterodactyl_client_api_key']}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 404:
                return await ctx.reply("Invalid support code!")
            emb = disnake.Embed(
                color=disnake.Color.green(),
                title=f"Server Info",
                url=f"{config['pterodactyl_url']}/server/{server_id}"
            )
            res_json = response.json()
            emb.add_field(
                name="id", value=res_json["attributes"]["uuid"], inline=False)
            emb.add_field(name="Name", value=res_json
                          ['attributes']['name'], inline=False)
            emb.add_field(name="Location", value=res_json
                          ['attributes']['node'], inline=False)
            if res_json['attributes']['description'] != "":
                emb.add_field(name="Description", value=res_json[
                              'attributes']['description'], inline=False)
            emb.add_field(name="CPU", value=res_json
                          ['attributes']['limits']['cpu'], inline=False)
            emb.add_field(name="RAM", value=res_json[
                          'attributes']['limits']['memory'], inline=False)
            emb.add_field(name="Disk", value=res_json
                          ['attributes']['limits']['disk'], inline=False)
            if res_json['attributes']['is_suspended']:
                emb.add_field(name="Suspended", value="Yes", inline=False)

            await ctx.reply(embed=emb)
        except:
            await ctx.reply("Failed to get server info for the server ID provided.")

    @commands.command(name="serverstatus")
    async def _serverstatus(self, ctx: commands.Context, server_id="null"):
        if server_id == 'null':
            return await ctx.reply("Please enter the support code.")
        url = f"{config['pterodactyl_url']}/api/client/servers/{server_id}/resources"
        headers = {
            "Authorization": f"Bearer {config['pterodactyl_client_api_key']}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 404:
                return await ctx.reply("Invalid support code!")
            res_json = response.json()
            if response.status_code == 409:
                return await ctx.reply("This server is suspended!")
            col = disnake.Color.dark_gray()
            if res_json['attributes']['current_state'] == 'starting':
                col = disnake.Color.yellow()
            elif res_json['attributes']['current_state'] == 'running':
                col = disnake.Color.green()
            elif res_json['attributes']['current_state'] == 'stopping':
                col = disnake.Color.orange()
            elif res_json['attributes']['current_state'] == 'offline':
                col = disnake.Color.red()
            emb = disnake.Embed(
                color=col,
                title=f"Server Status",
                url=f"{config['pterodactyl_url']}/server/{server_id}"
            )
            emb.add_field(
                name="status", value=res_json['attributes']['current_state'], inline=False)
            if res_json['attributes']['current_state'] == 'offline':
                return await ctx.reply(embed=emb)
            emb.add_field(
                name="RAM Usage", value=res_json['attributes']['resources']['memory_bytes'] / 1024 / 1024, inline=False
            )
            emb.add_field(
                name="CPU Usage", value=res_json['attributes']['resources']['cpu_absolute'], inline=False
            )
            emb.add_field(
                name="Disk usage", value=res_json['attributes']['resources']['disk_bytes'] / 1024 / 1024, inline=False
            )
            await ctx.reply(embed=emb)
        except:
            await ctx.reply("Failed to get server info for the server ID provided.")


def setup(bot: commands.Bot):
    bot.add_cog(pterodactyl_Commands(bot))
