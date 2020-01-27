from discord.ext import commands
from rubybot.utils import llparser
from seiutils import linkutils, discordutils

MAX_CHAR = 2000

class Info(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def lyrics(self, ctx):
        pass

    async def send_lyrics(self, ctx, lyrics):
        if len(lyrics) > MAX_CHAR:
            split = lyrics.split('\n\n')
            str = ''
            for verse in split:
                if len(str) + len(verse) + 2 < MAX_CHAR:
                    str += verse + '\n\n'
                else:
                    await ctx.send(str)
                    str = verse + '\n\n'
            
            if len(str) > 0:
                await ctx.send(str)
        else:
            await ctx.send(lyrics)

    @lyrics.command()
    async def en(self, ctx, *, title):
        lyrics = llparser.get_lyrics(title, lang=llparser.EN)
        if lyrics is None:
            await ctx.send(f'Could not find song {title}')
        else:
            await self.send_lyrics(ctx, lyrics)

    @lyrics.command()
    async def romaji(self, ctx, *, title):
        lyrics = llparser.get_lyrics(title, lang=llparser.ROMAJI)
        if lyrics is None:
            await ctx.send(f'Could not find song {title}')
        else:
            await self.send_lyrics(ctx, lyrics)

def setup(bot):
    bot.add_cog(Info(bot))


