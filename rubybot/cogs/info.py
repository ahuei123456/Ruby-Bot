import asyncio

from discord.ext import commands
from cogs.utils import utilities
from cogs.utils import llparser
from cogs.utils import twitconn


class Info:
    max_char = 2000
    buffer = 5
    code_block = '```'
    loop = None

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
        await self.get_lyrics(title, self.llparser.lyrics_lang[0])

    @lyrics.command(name='kanji', pass_context=True)
    async def kanji(self, ctx, *, title: str):
        """
        Retrieves lyrics of a Love Live! song in Kanji.
        :param title: Title of the song to retrieve lyrics for. Currently, the match must be exact with the title given on the wikia.
        """
        await self.get_lyrics(title, self.llparser.lyrics_lang[1])

    @lyrics.command(name='english', pass_context=True)
    async def english(self, ctx, *, title: str):
        """
        Retrieves lyrics of a Love Live! song in English.
        :param title: Title of the song to retrieve lyrics for. Currently, the match must be exact with the title given on the wikia.
        """
        await self.get_lyrics(title, self.llparser.lyrics_lang[2])

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

    @commands.command(name='twit')
    async def twit(self, *, id: str):
        """
        Retrieves basic information about a twitter user.
        :param id: Username of the user to retrieve info from
        """
        try:
            info = twitconn.get_user_info(id)
            await self.bot.say(info)
        except Exception as e:
            await self.bot.say(e)

    @commands.command(name='stream', pass_context=True, no_pm=True, hidden=True)
    async def stream(self, ctx):
        if ctx.message.author.id == '144803988963983360':
            if self.loop is None:
                await self.bot.say('Now stalking')
                self.loop = asyncio.get_event_loop()
                self.loop.create_task(self.tweet_retriever(ctx.message.channel))
            else:
                await self.bot.say('Ending stalking')
                self.stop_loop = True
                self.loop = None

    async def tweet_retriever(self, channel):
        await self.bot.wait_until_ready()
        self.stop_loop = False
        while not self.stop_loop:
            statuses = twitconn.stream_new_tweets()
            while len(statuses) > 0:
                await self.bot.send_message(channel, statuses.pop(0))
            await asyncio.sleep(5)

    @commands.command(name='twit_id', hidden=True)
    async def print_id(self, twitter_id: str):
        try:
            await self.bot.say(twitconn.get_user_id(twitter_id))
        except Exception as e:
            await self.bot.say(e)



def setup(bot):
    bot.add_cog(Info(bot))


