import requests
import bs4
import codecs

from discord.ext import commands


class Lyrics:

    ll_ids = ('Full_Unit_Singles', 'Printemps', 'BiBi', 'lily_white', 'Mermaid_festa_vol.2_.7EPassionate.7E', 'Otome_Shiki_Ren.27ai_Juku', 'Kokuhaku_Biyori.2C_desu.21', 'soldier_game' , 'Kousaka_Honoka_Solos', 'Sonoda_Umi_Solos', 'Minami_Kotori_Solos')
    ss_ids = ('Full_Unit_Singles', 'CYaRon.21', 'AZALEA', 'Guilty_Kiss')
    base = 'http://love-live.wikia.com'

    title = 'title'
    link = 'link'

    lang = ('romaji', 'kanji', 'english')

    links = dict()
    code_block = '```'

    max_char = 2000
    buffer = 5

    def __init__(self, bot):
        self.bot = bot
        self.ll_crawl()
        self.ss_crawl()

    def ll_crawl(self):
        ll = requests.get(self.base + '/wiki/Love_Live!').content
        ll_soup = bs4.BeautifulSoup(ll, 'html.parser')

        #subunits + duo/trio
        for x in range(0, len(self.ll_ids)):
            if x == 0:
                #special case for full unit singles
                data_01 = ll_soup.find(
                    id=self.ll_ids[0]).parent.next_sibling.next_sibling.next_sibling.next_sibling.children
            else:
                data_01 = ll_soup.find(id=self.ll_ids[x]).parent.next_sibling.next_sibling.children
            for child in data_01:
                data_02 = child.find('ol')
                if not (data_02 == -1 or data_02 is None):
                    for title in data_02.children:
                        for obj in title:
                            if len(obj.string.strip()) > 0:
                                try:
                                    self.links[obj.string] = obj.attrs['href']
                                except AttributeError:
                                    pass

    def ss_crawl(self):
        ss = requests.get(self.base + '/wiki/Love_Live!_Sunshine!!').content
        ss_soup = bs4.BeautifulSoup(ss, 'html.parser')
        for x in range(0, len(self.ss_ids)):
            if x == 0:
                # special case for full unit singles
                data_01 = ss_soup.find(
                    id=self.ss_ids[0]).parent.next_sibling.next_sibling.next_sibling.next_sibling.children
            else:
                data_01 = ss_soup.find(id=self.ss_ids[x]).parent.next_sibling.next_sibling.children
            for child in data_01:
                data_02 = child.find('ol')
                if not (data_02 == -1 or data_02 is None):
                    for title in data_02.children:
                        for obj in title:
                            if len(obj.string.strip()) > 0:
                                try:
                                    self.links[obj.string] = obj.attrs['href']
                                except AttributeError:
                                    pass

    @commands.group(name='lyrics', pass_context=True, invoke_without_command=True)
    async def lyrics(self, ctx, *, title:str):
        """
        Retrieves lyrics of a Love Live! song. Defaults to romaji if no language is specified.
        :param title: Title of the song to retrieve lyrics for. Currently, the match must be exact with the title given on the wikia.
        """
        print(title)
        if ctx.invoked_subcommand is None:
            await self.get_lyrics(title)

    @lyrics.command(name='romaji', pass_context=True)
    async def romaji(self, ctx, *, title:str):
        """
        Retrieves lyrics of a Love Live! song in Romaji.
        :param title: Title of the song to retrieve lyrics for. Currently, the match must be exact with the title given on the wikia.
        """
        await self.get_lyrics(title, self.lang[0])

    @lyrics.command(name='kanji', pass_context=True)
    async def kanji(self, ctx, *, title: str):
        """
        Retrieves lyrics of a Love Live! song in Kanji.
        :param title: Title of the song to retrieve lyrics for. Currently, the match must be exact with the title given on the wikia.
        """
        await self.get_lyrics(title, self.lang[1])

    @lyrics.command(name='english', pass_context=True)
    async def english(self, ctx, *, title: str):
        """
        Retrieves lyrics of a Love Live! song in English.
        :param title: Title of the song to retrieve lyrics for. Currently, the match must be exact with the title given on the wikia.
        """
        await self.get_lyrics(title, self.lang[2])

    async def get_lyrics(self, title:str, language:str=lang[0]):
        title = title.strip()
        if title not in self.links.keys():
            await self.bot.say(
                "Sorry, please input an exact title (from the wikia) for now! This will be updated in the future, don't worry!")
            return
        link = self.links[title]
        link = self.base + link
        song = requests.get(link).content
        song_soup = bs4.BeautifulSoup(song, 'html.parser')

        index = self.lang.index(language)

        data_01 = song_soup.find_all(class_='poem')
        await self.msg_lyrics(data_01[index].get_text().split('\n\n'), title=title, link=link)

    async def msg_lyrics(self, lyrics:list, **kwargs):
        header = ''
        keys = list(kwargs.keys())
        if self.title in keys:
            header += kwargs[self.title] + ' '
        if self.link in keys:
            header += '<' + kwargs[self.link] + '>'

        if len(header) > 0:
            header = header.strip() + '\n'

        msg = ''
        for para in lyrics:
            if len(msg) + len(para) + len(header) < self.max_char - len(self.code_block) * 2 - self.buffer:
                msg += para + '\n\n'
            else:
                await self.bot.say('\n'.join((header, self.code(msg.strip()))).strip())
                msg = para + '\n\n'
                header = ''
        if len(msg) > 0:
            await self.bot.say((header + '\n' + self.code(msg.strip())).strip())

    def code(self, msg):
        return self.code_block + msg + self.code_block
