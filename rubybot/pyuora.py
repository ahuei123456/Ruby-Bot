import tweepy
import requests
import re
import bs4
import random
import codecs
from discord.ext import commands
from instagram import InstagramAPI


class Pyuora:

    api_twitter = None
    api_insta = None

    def __init__(self, bot):
        self.bot = bot

        self.init_twitter(r'files\twitter.txt')
        self.init_insta(r'files\insta.txt')


    @commands.command(name='mimo', pass_context=True, no_pm=True)
    async def mimo(self, ctx):
        """
        Displays @mimori_suzuko's current profile image and banner.
        """
        mimorin = self.api_twitter.get_user('mimori_suzuko')
        await self.bot.say("{0}'s current profile image is: {1}".format(mimorin.name, mimorin.profile_image_url.replace('_normal', '')))
        await self.bot.say("{0}'s current banner image is: {1}".format(mimorin.name, mimorin.profile_banner_url.replace('_normal', '')))

    @commands.command(name='tsun', no_pm=True)
    async def tsun(self, *, index: str = ''):
        """
        Displays a post from tsuntsunlive's Instagram.
        Original code taken from Chezz at https://github.com/chesszz/MemeBot/blob/master/MemeBot.py
        :param index: If an index is specified, the specific post on the front page is retrieved. If not, a random post is grabbed.
        """
        msgs = self.get_tsun(index)
        print(dir(feed))
        for msg in msgs:
            await self.bot.say(msg)

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

    def init_twitter(self, filename: str):
        data = open(filename)
        comp = list()
        for line in data:
            comp.append(line.strip())

        c_key = comp[0]
        c_secret = comp[1]
        a_token = comp[2]
        a_secret = comp[3]
        auth = tweepy.OAuthHandler(c_key, c_secret)
        auth.set_access_token(a_token, a_secret)

        self.api_twitter = tweepy.API(auth)

    def init_insta(self, filename: str):
        data = open(filename)
        comp = list()
        for line in data:
            comp.append(line.strip())

        access_token = comp[2]
        client_secret = comp[1]
        self.api_insta = InstagramAPI(access_token=access_token, client_secret=client_secret)


