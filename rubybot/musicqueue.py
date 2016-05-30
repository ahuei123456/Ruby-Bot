import asyncio
import discord
import textparse
import random
import texttable
import dbconn

from discord.ext import commands


class MusicQueue:
    search_results = 'Here are the results of your search:'
    results_read = 'Here are the currently unanswered suggestions:'
    results_accepted = 'Here are the currently unfinished unanswered suggestions:'
    results_reject = 'Your request: "{0}" has been rejected for the following reason: {1}'
    results_accept = 'Your request: "{0}" has been accepted with the following comment: {1}'
    results_finish = 'Congratulations! Your request: "{0}" has been completed with the following remarks: {1}'
    error_excess_results = 'Your search for "{0}" returned too many results!'
    error_excess_results_generic = 'Your search returned too many results!'
    error_no_results = 'Your search for "{0}" returned no results!'
    error_suggestion_too_long = 'Your suggestion is too long! Please limit it to 160 characters.'
    error_invalid_code = 'The code you specified is in an invalid format!'
    error_invalid_id = 'The id you specified is in an invalid format!'
    delay_del_command = 3
    delay_del_play = 1
    delay_del_announcement = 30

    tbl_limit = 12

    tbl_song_info = ('Song Code', 'Song Title', 'Song Artist', 'Song Album')
    tbl_album_list = ('Album Name',)
    tbl_suggest = ('ID', 'Creator', 'Suggestion', 'Status')

    code_block = '```'

    char_limit_suggest = 160

    def __init__(self, bot):
        self.bot = bot
        self.song_play = '!play'

        self.id_admin = '144803988963983360'

    @commands.command(pass_context=True, no_pm=True, hidden=True)
    async def title(self, ctx, *, title: str):
        """Deprecated. Use db title <title> instead"""
        await self.bot.say(self.code("Deprecated. Use db title <title> instead."))

    @commands.command(pass_context=True, no_pm=True, hidden=True)
    async def code(self, ctx, *, code: str):
        """Deprecated. Use db code <code> instead"""
        await self.bot.say(self.code("Deprecated. Use db code <code> instead."))

    @commands.command(pass_context=True, no_pm=True, hidden=True)
    async def album(self, ctx, *, album: str):
        """Deprecated. Use db album <album> instead"""
        await self.bot.say(self.code("Deprecated. Use db album <album> instead."))

    @commands.command(pass_context=True, no_pm=True, hidden=True)
    async def adv(self, ctx, *, adv: str):
        """Deprecated. Use db search <search args> instead"""
        await self.bot.say(self.code("Deprecated. Use db search <search args> instead."))

    @commands.group(name='db', pass_context=True, no_pm=True)
    async def db(self, ctx):
        """
        Lets you queue songs from within Ruby Bot's database.
        """
        pass

    @db.command(name='title', pass_context=True, no_pm=True)
    async def title(self, ctx, *, title: str):
        """Searches the music database by title for a song.
        Queues it if a single matching song is found.
        If multiple songs match the search term, a list of matching titles is displayed.
        :param title: Song title to search for
        """

        output = textparse.fix_input(title)
        data = textparse.title(output)
        if len(data) == 0:
            await self.error_results_not_found(title)
        else:
            await self.process(ctx, data)

    @db.command(name='album', pass_context=True, no_pm=True)
    async def album(self, ctx, *, album: str):
        """Searches the music database by title for an album.
        Queues all of it if a single matching album is found.
        If multiple albums match the search term, a list of matching albums is displayed.
        :param album: Song album to search for
        """
        output = textparse.fix_input(album)
        albums = textparse.albums(output)
        if len(albums) > 1:
            await self.print_table(ctx, self.error_excess_results.format(output), albums, self.tbl_album_list)
        elif len(albums) == 0:
            await self.error_results_not_found(album)
        else:
            data = textparse.album(output)
            await self.process(ctx, data, len(data))

    @db.group(name='anime', pass_context=True, no_pm=True)
    async def anime(self, ctx, *, anime: str):
        """
        Searches the music database for songs of an anime.
        Queues all the songs if an anime is found.
        :param anime: Title of anime
        """
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
        """
        Searches the music database by code for a song.
        Queues it if a single matching song is found.
        If no songs match the search term, an error is displayed.
        :param code: Song code to search for
        """
        output = textparse.fix_input(code)
        data = textparse.code(output)
        if len(data) == 0:
            await self.error_results_not_found(code)
        else:
            await self.process(ctx, data)

    @db.command(name='search', pass_context=True, no_pm=True)
    async def search(self, ctx, *, search: str):
        output = textparse.fix_input(search)
        data = textparse.adv(output)
        await self.process(ctx, data, len(data))

    @db.command(name='list', pass_context=True, no_pm=True)
    async def list(self, ctx, *, search: str=''):
        """
        Searches the music database using formatted arguments and PMs the info of all the songs found.
        :param search: A string containing arguments and parameters to search the database with. If no arguments are passed, all the songs in the database are PM'd.
        :return:
        """
        output = textparse.fix_input(search)
        data = textparse.adv(output)
        await self.pm_list(ctx, data)

    @db.command(name='download')
    async def download(self):
        """
        Retrieves the current music database.
        :return:
        """
        print('uploading')
        await self.bot.upload(fp='files\music.db', content='Current database:')

    # Suggestion commands from here onward
    @commands.command(name='suggest', pass_context=True, no_pm=True)
    async def suggest(self, ctx, *, suggestion: str):
        """
        Suggest something for the bot!
        :param suggestion: Your suggestion.
        """
        if ctx.invoked_subcommand is None:
            suggestion = suggestion.strip()
            if len(suggestion) <= 160:
                textparse.suggest(ctx.message.author.id, suggestion)
                await self.bot.say('Suggestion "{0}" has been added successfully!'.format(suggestion))
            else:
                await self.error_long_suggestion()

    @commands.command(name='read', pass_context=True, hidden=True)
    async def _read(self, ctx):
        if ctx.message.author.id == self.id_admin:
            data = textparse.read()
            print(data)
            await self.print_table(ctx, self.results_read, data, self.tbl_suggest, len(data), True)

    @commands.command(name='reject', pass_context=True, hidden=True)
    async def _reject(self, ctx, *, reason: str):
        if ctx.message.author.id == self.id_admin:
            data = reason.split()
            try:
                num = int(data[0])
                reason = ' '.join(data[1:])
                hunt = textparse.reject(num, reason)
                member = ctx.message.server.get_member(str(hunt[0]))
                if member is not None:
                    await self.bot.send_message(member, self.results_reject.format(hunt[1], hunt[2]))
            except TypeError:
                await self.bot.whisper(self.error_invalid_id)

    @commands.command(name='accept', pass_context=True, hidden=True)
    async def _accept(self, ctx, *, reason: str):
        if ctx.message.author.id == self.id_admin:
            data = reason.split()
            try:
                num = int(data[0])
                reason = ' '.join(data[1:])
                hunt = textparse.accept(num, reason)
                member = ctx.message.server.get_member(str(hunt[0]))
                if member is not None:
                    await self.bot.send_message(member, self.results_accept.format(hunt[1], hunt[2]))
            except TypeError:
                await self.bot.whisper(self.error_invalid_id)

    @commands.command(name='accepted', pass_context=True, hidden=True)
    async def _accepted(self, ctx):
        if ctx.message.author.id == self.id_admin:
            data = textparse.accepted()
            print(data)
            await self.print_table(ctx, self.results_accepted, data, self.tbl_suggest, len(data), True)

    @commands.command(name='finish', pass_context=True, hidden=True)
    async def _finish(self, ctx, *, reason: str):
        if ctx.message.author.id == self.id_admin:
            data = reason.split()
            try:
                num = int(data[0])
                reason = ' '.join(data[1:])
                hunt = textparse.finish(num, reason)
                member = ctx.message.server.get_member(str(hunt[0]))
                if member is not None:
                    await self.bot.send_message(member, self.results_finish.format(hunt[1], hunt[2]))
            except TypeError:
                await self.bot.whisper(self.error_invalid_id)

    async def pm_list(self, ctx, data):
        await self.print_table(ctx, self.search_results, self.get_song_info(data),
                               self.tbl_song_info, len(data), True)

    async def process(self, ctx, data, max_length=1):
        if len(data) <= max_length:
            await self.play_list(self.get_links(data))
            await asyncio.sleep(self.delay_del_command)
            await self.bot.delete_message(ctx.message)
        else:
            await self.print_table(ctx, self.error_excess_results, self.get_song_info(data),
                                   self.tbl_song_info, self.tbl_limit)

    async def error_long_suggestion(self):
        await self.bot.say(self.error_suggestion_too_long)

    async def error_results_not_found(self, search_term: str):
        await self.bot.say(self.error_no_results.format(search_term))

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
