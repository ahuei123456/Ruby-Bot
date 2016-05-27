import asyncio
import discord
import textparse
import random
import texttable
import dbconn

from discord.ext import commands


class MusicQueue:
    search_results = 'Here are the results of your search:'
    results_read = 'Here are the current unsolved suggestions:'
    error_excess_results = 'Your search returned too many results!'
    error_invalid_code = 'The code you specified is in an invalid format!'
    delay_del_command = 3
    delay_del_play = 1
    delay_del_announcement = 30

    tbl_limit = 12

    tbl_song_info = ('Song Code', 'Song Title', 'Song Artist', 'Song Album')
    tbl_album_list = ('Album Name',)
    tbl_suggest_read = ('ID', 'Creator', 'Suggestion', 'Status')

    code_block = '```'

    def __init__(self, bot):
        self.bot = bot
        self.song_play = '!play'

        self.id_admin = '144803988963983360'

    @commands.group(name='db', pass_context=True, no_pm=True)
    async def db(self, ctx):
        pass

    @db.command(name='title', pass_context=True, no_pm=True)
    async def title(self, ctx, *, title: str):
        """Searches the music database by title for a song.
        Queues it if a single matching song is found.
        If multiple songs match the search term, an error is displayed."""

        output = textparse.fix_input(title)
        data = textparse.title(output)
        await self.process(ctx, data)

    @db.command(name='album', pass_context=True, no_pm=True)
    async def album(self, ctx, *, album: str):
        """Searches the music database by title for an album.
        Queues all of it if a single matching album is found.
        If multiple albums match the search term, a list of matching albums is displayed."""
        output = textparse.fix_input(album)
        albums = textparse.albums(output)
        if len(albums) > 1:
            await self.print_table(ctx, self.error_excess_results, albums, self.tbl_album_list)
        else:
            data = textparse.album(output)
            await self.process(ctx, data, len(data))

    @db.group(name='anime', pass_context=True, no_pm=True)
    async def anime(self, ctx, *, anime: str):
        category = ''
        if anime.startswith('opening'):
            anime = anime.replace('opening', '', 1).strip()
            category = 'opening'
        elif anime.startswith('ending'):
            anime = anime.replace('ending', '', 1).strip()
            category = 'ending'
        output = textparse.fix_input(anime)
        data = textparse.anime(output, category)
        await self.process(ctx, data, len(data))

    @anime.command(name='opening', pass_context=True, no_pm=True)
    async def op(self, ctx, *, anime: str):
        """
        Searches the music database for opening songs of an anime.
        Queues all the openings if an anime is found.
        :param anime: Title of anime
        """


    @anime.command(name='ending', pass_context=True, no_pm=True)
    async def ed(self, ctx, *, anime: str):
        """
        Searches the music database for ending songs of an anime.
        Queues all the endings if an anime is found.
        :param anime: Title of anime
        """

    @db.command(name='code', pass_context=True, no_pm=True)
    async def _code(self, ctx, *, code: str):
        """Searches the music database by code for a song.
            Queues it if a single matching song is found.
            If multiple songs match the search term, an error is displayed."""
        output = textparse.fix_input(code)
        data = textparse.code(output)
        await self.process(ctx, data)

    @db.command(name='search', pass_context=True, no_pm=True)
    async def search(self, ctx, *, search: str):
        output = textparse.fix_input(search)
        data = textparse.adv(output)
        await self.process(ctx, data, len(data))

    @db.command(name='list', pass_context=True, no_pm=True)
    async def list(self, ctx, *, list: str):
        pass

    @commands.command(name='suggest', pass_context=True, no_pm=True)
    async def suggest(self, ctx, *, suggestion: str):
        if ctx.invoked_subcommand is None:
            textparse.suggest(ctx.message.author.id, suggestion)
            await self.bot.say('Suggestion "{0}" has been added successfully!'.format(suggestion))

    @commands.command(name='read', pass_context=True, hidden=True)
    async def _read(self, ctx):
        if ctx.message.author.id == self.id_admin:
            data = textparse.read()
            print(data)
            await self.print_table(ctx, self.results_read, data, self.tbl_suggest_read, len(data), True)


    async def process(self, ctx, data, max_length=1):
        if len(data) <= max_length:
            await self.play_list(self.get_links(data))
            await asyncio.sleep(self.delay_del_command)
            await self.bot.delete_message(ctx.message)
        else:
            await self.print_table(ctx, self.error_excess_results, self.get_song_info(data),
                                   self.tbl_song_info, self.tbl_limit)

    async def print_table(self, ctx, msg, data, titles, limit=tbl_limit, pm=False):
        del_later = list()
        del_later.append(ctx.message)
        error = msg + '\n'
        msg = None
        if len(data) <= limit:

            table = [titles]

            for row in data:
                table.append(row)

            output = texttable.print_table(table, 1994 - len(error))
            for x in range(0, len(output)):
                if x == 0:
                    error = self.code(error + output[x])
                else:
                    error = self.code(output[x])

                if pm:
                    await self.bot.whisper(error)
                else:
                    msg = await self.bot.say(error)
                    del_later.append(msg)

        else:
            error = self.code(error)
            if pm:
                await self.bot.whisper(error)
            else:
                msg = await self.bot.say(error)
                del_later.append(msg)

        await asyncio.sleep(self.delay_del_announcement)
        for msg in del_later:
            await self.bot.delete_message(msg)

    async def play_list(self, link_list):
        for link in link_list:
            await self.play_song(link)

    async def play_song(self, link):
        msg = await self.bot.say(self.song_play + ' ' + link)
        await asyncio.sleep(self.delay_del_play)
        await self.bot.delete_message(msg)

    def code(self, msg):
        return self.code_block + msg + self.code_block

    def get_links(self, full_list):
        links = list()

        for row in full_list:
            links.append(row[dbconn.columns.index('link')])

        return links

    def get_song_info(self, full_list):
        info = list()

        for row in full_list:
            _info = list()
            _info.append(row[dbconn.columns.index('code')])
            _info.append(row[dbconn.columns.index('title')])
            _info.append(row[dbconn.columns.index('artist')])
            _info.append(row[dbconn.columns.index('album')])

            info.append(_info)

        return info
