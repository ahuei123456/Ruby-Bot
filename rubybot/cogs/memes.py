import requests
import bs4
import re
import random
import codecs
import os

from discord.ext import commands
from cogs.utils import checks

path_qaz = os.path.join(os.getcwd(), 'files', 'qaz.txt')
path_riko = os.path.join(os.getcwd(), 'files', 'riko_meme')

class Memes:

    def __init__(self, bot):
        self.bot = bot
        self.init_qaz()
        self.init_riko()

    def init_qaz(self):
        self.filename = path_qaz
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

    def init_riko(self):
        self.riko_memes = os.listdir(path_riko)

    @commands.command(name='tsun', no_pm=True)
    async def tsun(self, *, index: str=''):
        """
        Displays a post from tsuntsunlive's Instagram.
        Original code taken from Chezz at https://github.com/chesszz/MemeBot/blob/master/MemeBot.py
        :param index: If an index is specified, the specific post on the front page is retrieved. If not, a random post is grabbed.
        """
        msgs = self.get_tsun(index)
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

    @commands.group(pass_context=True, no_pm=True)
    async def qaz(self, ctx):
        """
        Lets you save dank qaz quotes.
        If a subcommand is not called, a random qaz quote is displayed.
        """

        if ctx.invoked_subcommand is None:
            tags = list(self.qaz_list.keys())
            await self.bot.say(self.qaz_list[tags[random.randrange(0, len(tags))]])

    @qaz.command(pass_context=True, no_pm=True)
    async def add(self, ctx, name, *, link):
        """
        Adds a qaz quote to the database.
        :param name: Name of the qaz quote
        :param link: Content of the qaz quote
        """
        tag = name
        if tag not in list(self.qaz_list.keys()):
            print(self.qaz_file.write('\n' + link + ' ' + tag))
            self.qaz_file.flush()
            self.qaz_list[tag] = link
            await self.bot.say('Tag added successfully!')
        else:
            await self.bot.say('That tag already exists!')

    @qaz.command(name='list', pass_context=True, no_pm=True)
    async def _list(self, ctx):
        """
        Displays a list of all saved qaz quotes.
        """
        await self.bot.say(list(self.qaz_list.keys()))

    @commands.group(name='riko', pass_context=True, invoke_without_command=True)
    async def riko(self, ctx, filename=""):
        """
        Uploads a Riko meme.
        Chooses a random meme if filename is not specified.
        :param filename: Filename of the meme.
        """
        if ctx.invoked_subcommand is None:
            await self.upload_riko(filename)

    @riko.command(name='list')
    async def r_list(self):
        await self.bot.say('There are currently {} Riko memes!'.format(str(len(self.riko_memes))))

    @riko.command(name='refresh', pass_context=True)
    @checks.is_owner()
    async def r_refresh(self, ctx):
        self.init_riko()
        await self.bot.say('Database refreshed!')

    async def upload_riko(self, filename):
        if not filename in self.riko_memes:
            filename = self.riko_memes[random.randrange(0, len(self.riko_memes))]
        await self.bot.upload(fp=os.path.join(path_riko, filename), content=filename)
        print('uploaded riko meme')


def setup(bot):
    bot.add_cog(Memes(bot))
