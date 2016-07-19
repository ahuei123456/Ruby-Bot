import asyncio
import codecs

from discord.ext import commands
from cogs.utils import llparser
from cogs.utils import twitconn


class Info:
    max_char = 2000
    buffer = 5
    code_block = '```'
    loop = None
    spoil = list()

    def __init__(self, bot):
        self.bot = bot



    @commands.group(name='lyrics', pass_context=True, invoke_without_command=True)
    async def lyrics(self, ctx, *, title:str):
        """
        Retrieves lyrics of a Love Live! song. Defaults to romaji if no language is specified.
        :param title: Title of the song to retrieve lyrics for. Currently, the match must be exact with the title given on the wikia.
        """
        if ctx.invoked_subcommand is None:
            await self.get_lyrics(title)

    @lyrics.command(name='romaji', pass_context=True)
    async def romaji(self, ctx, *, title:str):
        """
        Retrieves lyrics of a Love Live! song in Romaji.
        :param title: Title of the song to retrieve lyrics for. Currently, the match must be exact with the title given on the wikia.
        """
        await self.get_lyrics(title, llparser.lyrics_lang[0])

    @lyrics.command(name='kanji', pass_context=True)
    async def kanji(self, ctx, *, title: str):
        """
        Retrieves lyrics of a Love Live! song in Kanji.
        :param title: Title of the song to retrieve lyrics for. Currently, the match must be exact with the title given on the wikia.
        """
        await self.get_lyrics(title, llparser.lyrics_lang[1])

    @lyrics.command(name='english', pass_context=True)
    async def english(self, ctx, *, title: str):
        """
        Retrieves lyrics of a Love Live! song in English.
        :param title: Title of the song to retrieve lyrics for. Currently, the match must be exact with the title given on the wikia.
        """
        await self.get_lyrics(title, llparser.lyrics_lang[2])

    async def get_lyrics(self, title:str, language:str=None):
        try:
            msgs = self.parse_lyrics(llparser.get_lyrics(title, language))
            for msg in msgs:
                await self.bot.say(msg)
        except ValueError as e:
            await self.bot.say(e)

    def parse_lyrics(self, info):
        msgs = list()
        header = ''
        header += info[0] + ' '
        header += '<' + info[1] + '>'

        if len(header) > 0:
            header = header.strip() + '\n'
        lyrics = info[2].split('\n\n')
        msg = ''
        for para in lyrics:
            if len(msg) + len(para) + len(header) < self.max_char - len(self.code_block) * 2 - self.buffer:
                msg += para + '\n\n'
            else:
                msgs.append('\n'.join((header, self.code(msg.strip()))).strip())
                msg = para + '\n\n'
                header = ''
        if len(msg) > 0:
            msgs.append((header + '\n' + self.code(msg.strip())).strip())

        return msgs

    def code(self, msg):
        return self.code_block + msg + self.code_block

    @commands.group(name='twit', pass_context=True, invoke_without_command=True)
    async def twit(self, ctx, *, id: str):
        """
        Retrieves basic information about a twitter user.
        :param id: Username of the user to retrieve info from
        """
        if ctx.invoked_subcommand is None:
            try:
                info = twitconn.get_user_info(id)
                await self.bot.say(info)
            except Exception as e:
                await self.bot.say(e)

    @twit.command(hidden=True)
    async def archive(self, id, filename):
        """
        Locally archives the last 200 tweets from a twitter user.
        :param id: Username of the user to archive tweets from
        :param filename: Filename to save archive to
        """
        twitconn.archive(id, filename)

    @commands.group()
    async def sif(self):
        pass

    @sif.command()
    async def card(self, num: int):
        pass

    @sif.command()
    async def song(self, *, title: str):
        result = llparser.get_song(title.strip())
        await self.bot.say(llparser.encode_song(result))

    @sif.group()
    async def event(self):
        pass

    @event.command(name='jp')
    async def event_jp(self, *, title: str):
        event = llparser.get_event(title.strip())
        await self.bot.say(llparser.encode_event_jp(event))

    @event.command(name='en')
    async def event_en(self, *, title: str):
        event = llparser.get_event(title.strip())
        await self.bot.say(llparser.encode_event_en(event))

    @sif.group()
    async def current(self):
        pass

    @current.command(name='jp')
    async def current_jp(self):
        event = llparser.current_event_jp()
        await self.bot.say(llparser.encode_current_jp(event))

    @current.command(name='en')
    async def current_en(self):
        event = llparser.current_event_en()
        await self.bot.say(llparser.encode_current_en(event))

    @commands.group(name='llss')
    async def llss(self):
        """
        LL! SS!! commands
        """
        msg = llparser.get_next_ep()
        await self.bot.say(msg)

    @llss.command(pass_context=True)
    async def spoil(self, ctx):
        pass

    @commands.command(name='archive', hidden=True)
    async def archive(self, *, hashtag):
        await self.bot.say('Archiving...')
        print('archiving')
        twitconn.save_hashtag('#' + hashtag)
        await self.bot.say('Done!')
        print('done')


def setup(bot):
    bot.add_cog(Info(bot))


