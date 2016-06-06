import asyncio

import discord
from discord.ext import commands

from cogs.utils import dbconn, texttable, utilities

if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus('opus')

class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, 'Now playing ' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()

class Music:
    search_results = 'Here are the results of your search:'
    error_excess_results = 'Your search for "{0}" returned too many results!'
    error_excess_results_generic = 'Your search returned too many results!'
    error_no_results = 'Your search for "{0}" returned no results!'

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
        self.voice_states = {}

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

        output = utilities.fix_input(title)
        data = utilities.title(output)
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
        output = utilities.fix_input(album)
        albums = utilities.albums(output)
        if len(albums) > 1:
            await self.print_table(ctx, self.error_excess_results.format(output), albums, self.tbl_album_list)
        elif len(albums) == 0:
            await self.error_results_not_found(album)
        else:
            data = utilities.album(output)
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
        output = utilities.fix_input(anime)
        data = utilities.anime(output, category)
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
        output = utilities.fix_input(code)
        data = utilities.code(output)
        if len(data) == 0:
            await self.error_results_not_found(code)
        else:
            await self.process(ctx, data)

    @db.command(name='search', pass_context=True, no_pm=True)
    async def search(self, ctx, *, search: str):
        output = utilities.fix_input(search)
        data = utilities.adv(output)
        await self.process(ctx, data, len(data))

    @db.command(name='list', pass_context=True, no_pm=True)
    async def list(self, ctx, *, search: str=''):
        """
        Searches the music database using formatted arguments and PMs the info of all the songs found.
        :param search: A string containing arguments and parameters to search the database with. If no arguments are passed, all the songs in the database are PM'd.
        """
        output = utilities.fix_input(search)
        data = utilities.adv(output)
        await self.pm_list(ctx, data)

    @db.command(name='download')
    async def download(self):
        """
        Retrieves the current music database.
        """
        print('uploading')
        await self.bot.upload(fp='files\music.db', content='Current database:')

    async def pm_list(self, ctx, data):
        await self.print_table(ctx, self.search_results, self.get_song_info(data),
                               self.tbl_song_info, len(data), True)

    async def process(self, ctx, data, max_length=1):
        if len(data) <= max_length:
            await self.play_list(ctx, self.get_links(data))
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
        if not pm:
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

    async def play_list(self, ctx, link_list):
        for link in link_list:
            await self.play_song(ctx, link)

    async def play_song(self, ctx, link):
        summoned_channel = self.bot.is_voice_connected(ctx.message.server)
        if not summoned_channel:
            msg = await self.bot.say(self.song_play + ' ' + link)
            await asyncio.sleep(self.delay_del_play)
            await self.bot.delete_message(msg)
        else:
            await self.queue_music(ctx, link)

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

    def find_member(self, id):
        id = str(id)
        servers = list(self.bot.servers)
        for server in servers:
            members = list(server.members)
            for member in members:
                if member.id == id:
                    return member

    def admin_message(self, msg):
        return msg.author.id == self.id_admin

    ######### PLAYLIST #########
    ######### MUSICBOT #########
    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx, *, channel: discord.Channel):
        """Joins a voice channel."""
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await self.bot.say('Already in a voice channel...')
        except discord.InvalidArgument:
            await self.bot.say('This is not a voice channel...')
        else:
            await self.bot.say('Ready to play audio in ' + channel.name)

    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say('You are not in a voice channel.')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song: str):
        """Plays a song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        await self.queue_music(ctx, song)

    async def queue_music(self, ctx, song: str):
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await self.bot.say('Enqueued ' + str(entry))
            await state.songs.put(entry)

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx, value: int):
        """Sets the volume of the currently playing song."""

        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            await self.bot.say('Set the volume to {:.0%}'.format(player.volume))

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        """Pauses the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """Resumes the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        """Stops playing audio and leaves the voice channel.
        This also clears the queue.
        """
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
        except:
            pass

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        """Vote to skip a song. The song requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('Not playing any music right now...')
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            await self.bot.say('Requester requested skipping song...')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                await self.bot.say('Skip vote passed, skipping song...')
                state.skip()
            else:
                await self.bot.say('Skip vote added, currently at [{}/3]'.format(total_votes))
        else:
            await self.bot.say('You have already voted to skip this song.')

    @commands.command(pass_context=True, no_pm=True)
    async def playing(self, ctx):
        """Shows info about the currently played song."""

        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            await self.bot.say('Not playing anything.')
        else:
            skip_count = len(state.skip_votes)
            await self.bot.say('Now playing {} [skips: {}/3]'.format(state.current, skip_count))

def setup(bot):
    bot.add_cog(Music(bot))
