from disnake.ext import commands


class PingCommand(commands.Cog):
    """Category for ping command."""

    def __init__(self, bot: commands.Bot):
        print("Loaded Ping Category")
        self.bot = bot

    @commands.command(name="ping")
    async def _ping(self, ctx: commands.Context):
        """Get the bot's current websocket latency."""
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)}ms")


def setup(bot: commands.Bot):
    bot.add_cog(PingCommand(bot))
