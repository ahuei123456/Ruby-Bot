import asyncio
import requests
import bs4
import re
import tweepy
import random
import codecs

from instagram import InstagramAPI
from discord.ext import commands
from cogs.utils import utilities
from cogs.utils import llparser


class LLWikiaListener(tweepy.StreamListener):

    def __init__(self, id):
        super(LLWikiaListener, self).__init__()

        self.statuses=list()
        self.id = id

    def on_status(self, status):

        if self.is_reply(status):
            return
        if not str(status.user.id) in self.id:
            return
        user = status.user.name
        text = status.text
        send = "Latest tweet by {0}: {1}\n".format(user, text)
        try:
            for media in status.extended_entities['media']:
                send += media['media_url'] + ' '
        except AttributeError:
            pass

        self.statuses.append(send)

    def is_reply(self, status):
        return status.in_reply_to_user_id is not None and status.in_reply_to_user_id != status.user.id

    def get_status(self):
        statuses = self.statuses[:]
        self.statuses.clear()
        return statuses


class Info:
    def __init__(self, bot):
        self.bot = bot
        self.llparser = llparser.LLParser()

        self.init_twitter()
        self.init_strim()

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
            msgs = self.llparser.get_lyrics(title, language)
            for msg in msgs:
                await self.bot.say(msg)
        except ValueError as e:
            await self.bot.say(e)

    @commands.command(name='mimo', pass_context=True, no_pm=True)
    async def mimo(self, ctx):
        """
        Displays @mimori_suzuko's current profile image and banner.
        """
        mimorin = self.api_twitter.get_user('mimori_suzuko')
        await self.bot.say("{0}'s current profile image is: {1}".format(mimorin.name,
                                                                        mimorin.profile_image_url.replace('_normal',
                                                                                                          '')))
        await self.bot.say("{0}'s current banner image is: {1}".format(mimorin.name,
                                                                       mimorin.profile_banner_url.replace('_normal',
                                                                                                          '')))

    @commands.command(name='tsun', no_pm=True)
    async def tsun(self, *, index: str = ''):
        """
        Displays a post from tsuntsunlive's Instagram.
        Original code taken from Chezz at https://github.com/chesszz/MemeBot/blob/master/MemeBot.py
        :param index: If an index is specified, the specific post on the front page is retrieved. If not, a random post is grabbed.
        """
        msgs = self.get_tsun(index)
        for msg in msgs:
            await self.bot.say(msg)

    @commands.command(name='yuyucm', no_pm=True)
    async def yuyucm(self, index: str = ''):
        """
        Gives a small introduction to our lovely Pure Oral Girl!
        """
        try:
            ind = int(index)
        except ValueError:
            index = None
        if index is None:
            shimu = self.api_twitter.get_user('yuyucm')
            await self.bot.say(
                "@yuyucm is the cutest 3D idol in the world!\nHer official twitter is <{0}> and her profile image is: {1}".format(
                    'https://twitter.com/yuyucm', shimu.profile_image_url.replace('_normal', '')))
        else:
            await self.send_media('yuyucm', ind)

    @commands.command(name='insti', no_pm=True)
    async def insti(self, index: str = ''):
        """
        Display a tweet from our lovely tumblr user!
        """
        try:
            ind = int(index)
        except ValueError:
            ind = 0

        await self.send_tweets('Instigare', ind)

    @commands.command(name='llwikia', pass_context=True, no_pm=True, hidden=True)
    async def llwikia(self, ctx):
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
            statuses = self.wikia_listener.get_status()
            while len(statuses) > 0:
                await self.bot.send_message(channel, statuses.pop(0))
            await asyncio.sleep(5)

    def get_tsun(self, index: str):
        r = requests.get('https://www.instagram.com/tsuntsunlive/')
        html = r.content
        soup = bs4.BeautifulSoup(html, 'html.parser')
        tag_list = soup.find_all("script", type="text/javascript")

        tag_list = [str(tag) for tag in tag_list]
        tag_list = sorted(tag_list, key=len)
        data_tag = tag_list[-1]

        after = index.split()
        try:
            index = int(after[0])
        except ValueError:
            index = None
        except IndexError:
            index = None

        post_list = re.split('"caption": "', data_tag)[1:]

        if index is None:
            post = random.choice(post_list)
        else:
            post = post_list[index - 1]

        caption = post[:re.search('", "likes"', post).start()]
        caption = re.sub(r"(\\u[0-9a-f]{4})", lambda match: codecs.decode(match.group(1), "unicode_escape"), caption)
        caption = re.sub(r"\\n", "\n", caption)

        img_part = post[re.search('"display_src": "', post).end():]
        img = img_part[:re.search("\?", img_part).start()]
        img = re.sub(r"\\", "", img)

        data = [img, caption]
        return data

    def init_twitter(self):
        credentials = utilities.load_credentials()

        c_key = credentials['client_key']
        c_secret = credentials['client_secret']
        a_token = credentials['access_token']
        a_secret = credentials['access_secret']
        self.auth = tweepy.OAuthHandler(c_key, c_secret)
        self.auth.set_access_token(a_token, a_secret)

        self.api_twitter = tweepy.API(self.auth)

    def init_insta(self, filename: str):
        data = open(filename)
        comp = list()
        for line in data:
            comp.append(line.strip())

        access_token = comp[2]
        client_secret = comp[1]
        self.api_insta = InstagramAPI(access_token=access_token, client_secret=client_secret)

    async def send_tweets(self, id: str, index: int = 0):
        statuses = self.get_tweets(id)

        if index >= len(statuses) - 1 or index <= 0:
            index = 1
        status = statuses[index - 1]
        await self.bot.say(status.text)

        urls = ''
        for url in self.get_media(status):
            urls += url + ' '

        urls = urls.strip()
        if len(urls) > 0:
            await self.bot.say(urls)

    async def send_tweet_with_media(self, id: str, index: int = 0):
        statuses = self.get_tweets(id)

        for status in statuses[:]:
            media_urls = self.get_media(status)
            if self.is_retweet(status) or self.is_reply(status) or len(media_urls) == 0:
                statuses.remove(status)

        if index >= len(statuses) - 1 or index <= 0:
            index = 1
        status = statuses[index - 1]
        await self.bot.say(status.text)

        urls = ''
        for url in self.get_media(status):
            urls += url + ' '

        urls = urls.strip()
        if len(urls) > 0:
            await self.bot.say(urls)

    async def send_media(self, id: str, index: int = 0):
        statuses = self.get_tweets(id)

        for status in statuses[:]:
            media_urls = self.get_media(status)
            if self.is_retweet(status) or self.is_reply(status) or len(media_urls) == 0:
                statuses.remove(status)

        if index >= len(statuses) - 1 or index <= 0:
            index = 1
        status = statuses[index - 1]

        urls = ''
        for url in self.get_media(status):
            urls += url + ' '

        urls = urls.strip()
        if len(urls) > 0:
            await self.bot.say(urls)

    def get_tweets(self, id: str):
        statuses = list(tweepy.Cursor(self.api_twitter.user_timeline, id=id).items(100))
        return statuses

    def is_retweet(self, status):
        return hasattr(status, 'retweeted_status')

    def is_reply(self, status):
        return status.in_reply_to_status_id is not None

    def get_media(self, status):
        media_urls = []

        if 'media' in status.entities:
            for media in status.entities['media']:
                media_urls.append(media['media_url'])

        return media_urls

    def test(self):
        statuses = list(tweepy.Cursor(self.api_twitter.user_timeline, id='mkyischy').items(50))
        # print(statuses[3].text)
        for item in dir(statuses[0]):
            print(item)
        #print((statuses[32].entities.keys()))
        #print(statuses[32].entities['media'])
        #print(self.get_media(statuses[31]))

    def init_strim(self):
        # llwikia 2734031000
        # mkydyrea 3299062544
        # ll_extra 739117766100189184
        id = ['2734031000', '3299062544']
        self.wikia_listener = LLWikiaListener(id)
        self.wikia_poster = tweepy.Stream(auth=self.auth, listener=self.wikia_listener)
        self.wikia_poster.filter(follow=id, async=True)
        self.loop = None

    @commands.command(name='twit_id', hidden=True)
    async def print_id(self, twitter_id: str):
        twitter_id = twitter_id.strip()
        try:
            insti = self.api_twitter.get_user(twitter_id)
            await self.bot.say(insti.id)
        except Exception as e:
            await self.bot.say(e)


def setup(bot):
    bot.add_cog(Info(bot))


