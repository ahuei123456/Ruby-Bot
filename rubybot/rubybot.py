import asyncio
import discord
import textparse
import random

from discord.ext import commands

info = 'Ruby Bot, your one-stop solution for music queueing! (Now updated with commands.ext)'

class Restricted:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context = True, no_pm = True)
    async def title(self, ctx, *, title:str):
        output = fix_input(title)
        await self.bot.say(textparse.title(output))

    @commands.command(pass_context = True, no_pm = True)
    async def code(self, ctx, *, code:str):
        output = fix_input(code)
        await self.bot.say(textparse.code(output))

    @commands.command(pass_context = True, no_pm = True)
    async def album(self, ctx, *, album:str):
        output = fix_input(album)
        await self.bot.say(textparse.album(output))

    @commands.command(pass_context = True, no_pm = True)
    async def adv(self, ctx, *, adv:str):
        output = fix_input(adv)
        await self.bot.say(str(output))

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
        
def fix_input(raw):
    text = raw.split()
    output = []
    build = ''
    for x in range(0, len(text)):
        string = text[x]
        
        if string in textparse.args:
            build = build.strip()
            if (len(build) > 0):
                output.append(build)
            output.append(string)
            build = ''
        elif len(build) == 0:
            if not string.startswith('"'):
                build += string
            else:
                # "food"
                if string.endswith('"'):
                    output.append(string[1:len(string) - 1])
                else:
                    build += ' ' + string[1:]
        else:
            if string.endswith('"'):
                build += string[:len(string) - 1]
                output.append(build.strip())
                build = ''
            else:
                build += ' ' + string
                
        
    if len(build) > 0:
        output.append(build.strip().rstrip())

    
    return output

bot = commands.Bot(command_prefix = commands.when_mentioned_or('~'), description = info )
bot.add_cog(Restricted(bot))
bot.add_cog(Qaz(bot, 'files\qaz.txt'))

@bot.event
async def on_ready():
    print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))

bot.run('MTc4Nzc3NjczOTExMjM4NjU2.ChIILw.pwa7cw7eM3nDrScoXTxOuifFuY4')
