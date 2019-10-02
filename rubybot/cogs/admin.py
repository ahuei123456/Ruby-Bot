from discord.ext import commands
from utilities import checks


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.is_owner()
    async def kill(self, ctx):
        await ctx.send("Bye bye")
        exit(0)


def setup(bot):
    bot.add_cog(Admin(bot))