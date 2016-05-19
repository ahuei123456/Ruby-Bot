import asyncio
import discord
import textparse
import random
import texttable

from discord.ext import commands

info = 'Ruby Bot, your one-stop solution for music queueing! (Now updated with commands.ext)'
excess_results = 'Your search returned too many results!'
com_del_delay = 3
post_del_delay = 1
ann_del_delay = 30

tbl_limit = 10

codeblock = '```'

class Music:

    def __init__(self, bot):
        self.bot = bot
        self.song_play = '!play'

    @commands.command(pass_context = True, no_pm = True)
    async def title(self, ctx, *, title:str):
        output = textparse.fix_input(title)
        data = textparse.title(output)
        await self.process(ctx, data)

    @commands.command(pass_context = True, no_pm = True)
    async def code(self, ctx, *, code:str):
        output = textparse.fix_input(code)
        data = textparse.code(output)
        await self.process(ctx, data)

    @commands.command(pass_context = True, no_pm = True)
    async def album(self, ctx, *, album:str):
        output = textparse.fix_input(album)
        data = textparse.album(output)
        await self.process(ctx, data, len(data))

    @commands.command(pass_context = True, no_pm = True)
    async def adv(self, ctx, *, adv:str):
        output = textparse.fix_input(adv)
        data = textparse.adv(output)
        await self.playlist(self.get_links(data))
        await asyncio.sleep(com_del_delay)
        await self.bot.delete_message(ctx.message)

    def get_links(self, fulllist):
        links = list()

        for row in fulllist:
            links.append(row[4])

        return links

    def strip_useless(self, fulllist):
        info = list()

        for row in fulllist:
            info.append(row[:4])

        return info

    async def process(self, ctx, data, max_length = 1):
        if len(data) <= max_length:
            await self.playlist(self.get_links(data))
            await asyncio.sleep(com_del_delay)
        else:
            del_later = list()
            error = codeblock + excess_results
            error += '\n'
            if len(data) <= tbl_limit:
                rows = self.strip_useless(data)
                titles = ('Song ID', 'Song Title', 'Song Artist', 'Song Album')
                table = [titles]

                for row in rows:
                    table.append(row)
                
                output = texttable.print_table(table, 1997 - len(error))
                for x in range(0, len(output)):
                    if x == 0:
                        error += output[x]
                        error += codeblock
                        msg = await self.bot.say(error)
                        del_later.append(msg)
                        
                    else:
                        error = codeblock + output[x] + codeblock
                        msg = await self.bot.say(error)
                        del_later.append(msg)
                        
                await asyncio.sleep(ann_del_delay)
                for msg in del_later:
                    await self.bot.delete_message(msg)
            else:
                error += codeblock
                msg = await self.bot.say(error)
                await asyncio.sleep(ann_del_delay)
                await self.bot.delete_message(msg)
        
        await self.bot.delete_message(ctx.message)
    
    async def playlist(self, linklist):
        for link in linklist:
            await self.playsong(link)
    
    async def playsong(self, link):
        msg = await self.bot.say(self.song_play + ' ' + link)
        await asyncio.sleep(post_del_delay)
        await self.bot.delete_message(msg)

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
        if ctx.invoked_subcommand is None:
            tags = list(self.qaz_list.keys())
            await self.bot.say(self.qaz_list[tags[random.randrange(0, len(tags))]])

    @qaz.command(pass_context = True, no_pm = True)
    async def add(self, ctx, *msg:str):
        data = textparse.fix_input(str(msg), None)
        print(msg)
        tag = data[1]
        link = data[0]
        if (tag not in list(self.qaz_list.keys())):
            self.qaz_file.write('\n' + link + ' ' + tag)
            self.qaz_list[tag] = link
            await self.bot.say('Tag added successfully!')
        else:
            await self.bot.say('That tag already exists!')

bot = commands.Bot(command_prefix = commands.when_mentioned_or('~'), description = info )
bot.add_cog(Music(bot))
bot.add_cog(Qaz(bot, 'files\qaz.txt'))

@bot.event
async def on_ready():
    print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))

bot.run('MTc4Nzc3NjczOTExMjM4NjU2.ChIILw.pwa7cw7eM3nDrScoXTxOuifFuY4')
