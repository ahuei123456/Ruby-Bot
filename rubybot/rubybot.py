import asyncio
import discord
import textparse
import random
import texttable

from discord.ext import commands

info = 'Ruby Bot, your one-stop solution for music queueing! (Now updated with commands.ext)'
excess_results = 'Your search returned too many results!'
search_results = 'Here are the results of your search:'
com_del_delay = 3
post_del_delay = 1
ann_del_delay = 30

tbl_limit = 12

codeblock = '```'

flag_find = '-f'

class Music:

    def __init__(self, bot):
        self.bot = bot
        self.song_play = '!play'

    @commands.command(pass_context = True, no_pm = True)
    async def title(self, ctx, *, title:str):
        """Searches the music database by title for a song.
Queues it if a single matching song is found.
If multiple songs match the search term, an error is displayed."""
        output = textparse.fix_input(title)
        pm = self.contains_find(output)
        data = textparse.title(output)
        if pm:
            await self.print_table(ctx, search_results, self.strip_useless(data), ('Song Code', 'Song Title', 'Song Artist', 'Song Album'), 600, True)
        else:
            await self.process(ctx, data)

    @commands.command(pass_context = True, no_pm = True)
    async def code(self, ctx, *, code:str):
        """Searches the music database by code for a song.
Queues it if a single matching song is found.
If multiple songs match the search term, an error is displayed."""
        output = textparse.fix_input(code)
        data = textparse.code(output)
        await self.process(ctx, data)

    @commands.command(pass_context = True, no_pm = True)
    async def album(self, ctx, *, album:str):
        """Searches the music database by title for an album.
Queues all of it if a single matching album is found.
If multiple songs match the search term, an album is displayed."""
        output = textparse.fix_input(album)
        albums = textparse.albums(output)
        if len(albums) > 1:
            await self.print_table(ctx, excess_results, albums, ('Album Name',), tbl_limit)
        else:    
            data = textparse.album(output)
            await self.process(ctx, data, len(data))

    @commands.command(pass_context = True, no_pm = True)
    async def adv(self, ctx, *, adv:str):
        """Sekrit command do not use"""
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

    def contains_find(self, data):
        if flag_find in data:
            data.remove(flag_find)
            return True
        return False
    
    async def process(self, ctx, data, max_length = 1):
        if len(data) <= max_length:
            await self.playlist(self.get_links(data))
            await asyncio.sleep(com_del_delay)
            await self.bot.delete_message(ctx.message)
        else:
            await self.print_table(ctx, excess_results, self.strip_useless(data), ('Song Code', 'Song Title', 'Song Artist', 'Song Album'), tbl_limit)

    async def print_table(self, ctx, msg, data, titles, limit = tbl_limit, pm = False):
        del_later = list()
        del_later.append(ctx.message)
        error = codeblock + msg
        error += '\n'
        msg = None
        if len(data) <= limit:
                
            table = [titles]

            for row in data:
                table.append(row)
                
            output = texttable.print_table(table, 1997 - len(error))
            for x in range(0, len(output)):
                if x == 0:
                    error += output[x]
                    error += codeblock
                else:
                    error = codeblock + output[x] + codeblock
                if pm:await self.bot.whisper(error)
                else:
                    msg = await self.bot.say(error)
                del_later.append(msg)
                        
            await asyncio.sleep(ann_del_delay)
            for msg in del_later:
                await self.bot.delete_message(msg)
        else:
            error += codeblock
            if pm:await self.bot.whisper(error)
            else:
                msg = await self.bot.say(error)
            await asyncio.sleep(ann_del_delay)
            await self.bot.delete_message(msg)
        
    
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


bot = commands.Bot(command_prefix = commands.when_mentioned_or('~'), description = info )
bot.add_cog(Music(bot))
bot.add_cog(Qaz(bot, 'files\qaz.txt'))
token_file = open(r'files\token.txt', 'r')
token = token_file.read().strip()
token_file.close()

@bot.event
async def on_ready():
    print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))


bot.run(token)
