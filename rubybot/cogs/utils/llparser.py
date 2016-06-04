import requests
import bs4
import re

class LLParser:
    swaps = {'Blueberry Train': 'Blueberry♥Train', 'Gay Garden': 'Garasu no Hanazono',
             'Susume Tomorrow': 'Susume→Tomorrow',
             'Susume->Tomorrow': 'Susume→Tomorrow', 'Start Dash!!': 'START:DASH!!', 'Music Start': 'Music S.T.A.R.T!!',
             'Kira Kira Sensation': 'KiRa-KiRa Sensation!', 'Shangrila Shower': 'Shangri-La Shower',
             'Mi wa Music no Mi': "Mi wa Mu'sic no Mi'", 'Super LOVE Super LIVE': 'Super LOVE=Super LIVE!',
             '?<-Heartbeat': '？←HEARTBEAT', 'Hatena Heartbeat': '？←HEARTBEAT',
             'Bokuhika': 'Bokutachi wa Hitotsu no Hikari',
             'puwapuwao': 'Puwa Puwa-O!', 'puwapuwa o': 'Puwa Puwa-O!', 'itsudemo': 'Eien Friends',
             'waowao powerful day': 'WAO-WAO Powerful day!',
             'wao wao powerful day': 'WAO-WAO Powerful day!', 'Anone ganbare': 'A-NO-NE-GA-N-BA-RE!',
             "OtomeShiki Renai Juku": "Otome Shiki Ren'ai Juku ", "Aqours HEROES": "Aqours☆HEROES",
             "Step ZERO to ONE": "Step! ZERO to ONE"}

    wikia_base = 'http://love-live.wikia.com'
    wikia_pages = ('/wiki/Love_Live!', '/wiki/Love_Live!_Sunshine!!')
    lyrics_lang = ('romaji', 'kanji', 'english')

    links = dict()
    title = 'title'
    link = 'link'


    eng_jp = dict()


    max_char = 2000
    buffer = 5
    code_block = '```'

    def __init__(self):
        self.wikia_crawl()

    def wikia_crawl(self):
        for sites in self.wikia_pages:
            ll = requests.get(self.wikia_base + sites).content
            ll_soup = bs4.BeautifulSoup(ll, 'html.parser')

            lists = ll_soup.find_all('ol')
            for data_02 in lists:
                for data_03 in data_02:
                    if not (data_03 == -1 or data_03 is None):
                        for title in data_03.children:
                            obj = title
                            try:
                                if len(obj.string.strip()) > 1 and 'href' in list(obj.attrs.keys()):
                                    try:
                                        self.links[obj.string] = obj.attrs['href']
                                        self.swaps[obj.string] = obj.string
                                    except AttributeError:
                                        pass
                            except AttributeError:
                                continue

    def sif_crawl(self):
        pass

    def get_lyrics(self, title: str, language: str = lyrics_lang[0]):
        title = self.sub_title(title)
        print(title)
        if title not in self.links.keys():
            raise ValueError('Sorry, song title was not found!')
        link = self.links[title]
        link = self.wikia_base + link
        song = requests.get(link).content
        song_soup = bs4.BeautifulSoup(song, 'html.parser')

        if language is None:
            index = 0
        else:
            index = self.lyrics_lang.index(language)

        data_01 = song_soup.find_all(class_='poem')
        return self.msg_lyrics(data_01[index].get_text().split('\n\n'), title=title, link=link)

    def msg_lyrics(self, lyrics: list, **kwargs):
        msgs = list()
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
                msgs.append('\n'.join((header, self.code(msg.strip()))).strip())
                msg = para + '\n\n'
                header = ''
        if len(msg) > 0:
            msgs.append((header + '\n' + self.code(msg.strip())).strip())

        return msgs

    def sub_title(self, title):
        regex = re.compile('.*' + title + '.*', re.IGNORECASE)

        for key in self.swaps.keys():
            if regex.match(key):
                return self.swaps[key]

    def code(self, msg):
        return self.code_block + msg + self.code_block
