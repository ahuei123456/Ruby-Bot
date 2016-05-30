import requests
import bs4
import re

from discord.ext import commands


class Lyrics:

    ll_ids = ('Full_Unit_Singles', 'Printemps', 'BiBi', 'lily_white', 'Mermaid_festa_vol.2_.7EPassionate.7E', 'Otome_Shiki_Ren.27ai_Juku', 'Kokuhaku_Biyori.2C_desu.21', 'soldier_game' , 'Kousaka_Honoka_Solos', 'Sonoda_Umi_Solos', 'Minami_Kotori_Solos', 'Love_Live.21_Web_Radio', 'Love_Live.21_TV_Anime_Blu-ray', 'Love_Live.21_TV_Anime_2_Blu-ray', 'Love_Live.21_Movie_Blu-ray', '.CE.BC.27s_.E2.86.92NEXT_LoveLive.21_2014_.7EENDLESS_PARADE.7E_Special_CD', '.CE.BC.27s_Go.E2.86.92Go.21_LoveLive.21_2015_.7EDream_Sensation.21.7E_Special_CD')
    ss_ids = ('Full_Unit_Singles', 'CYaRon.21', 'AZALEA', 'Guilty_Kiss')
    base = 'http://love-live.wikia.com'

    title = 'title'
    link = 'link'

    lang = ('romaji', 'kanji', 'english')

    links = dict()
    swaps = {'Blueberry Train':'Blueberry♥Train', 'Gay Garden':'Garasu no Hanazono', 'Susume Tomorrow':'Susume→Tomorrow',
             'Susume->Tomorrow':'Susume→Tomorrow', 'Start Dash!!':'START:DASH!!', 'Music Start':'Music S.T.A.R.T!!',
             'Kira Kira Sensation':'KiRa-KiRa Sensation!', 'Shangrila Shower':'Shangri-La Shower',
             'Mi wa Music no Mi':"Mi wa Mu'sic no Mi'", 'Super LOVE Super LIVE':'Super LOVE=Super LIVE!',
             '?<-Heartbeat':'？←HEARTBEAT', 'Hatena Heartbeat':'？←HEARTBEAT', 'Bokuhika':'Bokutachi wa Hitotsu no Hikari',
             'puwapuwao':'Puwa Puwa-O!', 'puwapuwa o':'Puwa Puwa-O!', 'itsudemo':'Eien Friends', 'waowao powerful day':'WAO-WAO Powerful day!',
             'wao wao powerful day':'WAO-WAO Powerful day!', 'Anone ganbare':'A-NO-NE-GA-N-BA-RE!', "OtomeShiki Ren'ai Juku":"Otome Shiki Ren'ai Juku "}
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
                try:
                    data_02 = child.find_all('ol')
                except AttributeError:
                    continue
                for data_03 in data_02:
                    if not (data_03 == -1 or data_03 is None):
                        for title in data_03.children:
                            for obj in title:
                                if len(obj.string.strip()) > 0:
                                    try:
                                        self.links[obj.string] = obj.attrs['href']
                                        self.swaps[obj.string] = obj.string
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
                                    self.swaps[obj.string] = obj.string
                                except AttributeError:
                                    pass

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
        title = self.sub_title(title)
        print(title)
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

    def sub_title(self, title):
        regex = re.compile('.*'+title+'.*', re.IGNORECASE)

        for key in self.swaps.keys():
            if regex.match(key):
                return self.swaps[key]


