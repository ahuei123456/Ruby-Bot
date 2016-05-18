import asyncio
import discord
import textparse
import random

from discord.ext import commands

info = 'Ruby Bot, your one-stop solution for music queueing! (Now updated with commands.ext)'

class Restricted:

    def __init__(self, bot):
        self.bot = bot
        self.song_play = '!play'

    @commands.command(pass_context = True, no_pm = True)
    async def title(self, ctx, *, title:str):
        output = textparse.fix_input(title)
        data = textparse.title(output)
        await self.playsong(data[0][4])

    @commands.command(pass_context = True, no_pm = True)
    async def code(self, ctx, *, code:str):
        output = textparse.fix_input(code)
        await self.bot.say(textparse.code(output))

    @commands.command(pass_context = True, no_pm = True)
    async def album(self, ctx, *, album:str):
        output = textparse.fix_input(album)
        await self.bot.say(textparse.album(output))

    @commands.command(pass_context = True, no_pm = True)
    async def adv(self, ctx, *, adv:str):
        output = textparse.fix_input(adv)
        await self.bot.say(str(output))

    async def playsong(self, link):
        msg = await self.bot.say(self.song_play + ' ' + link)
        await asyncio.sleep(2)
        await self.bot.delete_message(msg)

class Qaz:
    def __init__(self, bot, filename):
        self.bot = bot
        self.qaz_file = open(filename)
        self.qaz_list = list()
        
        for line in self.qaz_file:
            data = line.split()
            qaz_post = ''
            
            for block in data:
                if block.startswith('http'):
                    qaz_post += block + ' '
                else:
                    break

            self.qaz_list.append(qaz_post)

    @commands.command(pass_context = True, no_pm = True)
    async def qaz(self, ctx):
        await self.bot.say(self.qaz_list[random.randrange(0, len(self.qaz_list))])
        


bot = commands.Bot(command_prefix = commands.when_mentioned_or('~'), description = info )
bot.add_cog(Restricted(bot))
bot.add_cog(Qaz(bot, 'files\qaz.txt'))

@bot.event
async def on_ready():
    print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))

bot.run('MTc4Nzc3NjczOTExMjM4NjU2.ChIILw.pwa7cw7eM3nDrScoXTxOuifFuY4')
