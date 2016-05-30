import asyncio
import discord
import textparse
import random
import texttable
import musicqueue
import pyuora
import lyrics

from discord.ext import commands

info = "Ruby Bot, your one-stop solution for music queueing! (Now updated with commands.ext)\nNow updated with lyrical display! Use lyrics <title> to display the lyrics of any muse song.\nThank you for using Ruby Bot!"
excess_results = 'Your search returned too many results!'
search_results = 'Here are the results of your search:'
com_del_delay = 3
post_del_delay = 1
ann_del_delay = 30

tbl_limit = 12

class Qaz:
    def __init__(self, bot, filename):
        self.bot = bot
        self.filename = filename
        self.qaz_file = open(self.filename, 'r')
        self.qaz_list = dict()
        
        for line in self.qaz_file:
            data = line.split()
            qaz_post = ''
            qaz_tag = ''
            
            for block in data:
                if block.startswith('http'):
                    qaz_post += block + ' '
                else:
                    qaz_tag += block + ' '

            self.qaz_list[qaz_tag.strip()] = qaz_post.strip()
        self.qaz_file.close()
        self.qaz_file = open(self.filename, 'a')

    @commands.group(pass_context=True, no_pm=True)
    async def qaz(self, ctx):
        """Lets you save dank qaz quotes.
If a subcommand is not called, a random qaz quote is displayed."""
            
        if ctx.invoked_subcommand is None:
            tags = list(self.qaz_list.keys())
            await self.bot.say(self.qaz_list[tags[random.randrange(0, len(tags))]])

    @qaz.command(pass_context = True, no_pm = True)
    async def add(self, ctx, *msg:str):
        tag = msg[0]
        link = msg[1]
        if (tag not in list(self.qaz_list.keys())):
            print(self.qaz_file.write('\n' + link + ' ' + tag))
            self.qaz_file.flush()
            self.qaz_list[tag] = link
            await self.bot.say('Tag added successfully!')
        else:
            await self.bot.say('That tag already exists!')

    @qaz.command(name = 'list', pass_context = True, no_pm = True)
    async def _list(self, ctx):
        print(list(self.qaz_list.keys()))


bot = commands.Bot(command_prefix=commands.when_mentioned_or('~'), description=info)
bot.add_cog(Qaz(bot, 'files\qaz.txt'))
bot.add_cog(musicqueue.MusicQueue(bot))
bot.add_cog(pyuora.Pyuora(bot))
bot.add_cog(lyrics.Lyrics(bot))
token_file = open(r'files\token.txt', 'r')
token = token_file.read().strip()
token_file.close()

@bot.event
async def on_ready():
    print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))


bot.run(token)
