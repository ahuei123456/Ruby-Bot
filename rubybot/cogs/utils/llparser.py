import requests
import bs4
import re
import json

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
         "OtomeShiki Renai Juku": "Otome Shiki Ren'ai Juku", "Aqours HEROES": "Aqours☆HEROES",
         "Step ZERO to ONE": "Step! ZERO to ONE"}

wikia_base = 'http://love-live.wikia.com'
wikia_pages = ('/wiki/Love_Live!', '/wiki/Love_Live!_Sunshine!!', '/wiki/A-RISE')
lyrics_lang = ('romaji', 'kanji', 'english')

links = dict()
title = 'title'
link = 'link'

eng_jp = dict()

cards_url = 'http://schoolido.lu/api/cards/'
cache_url = 'http://schoolido.lu/api/cacheddata/'
event_url = 'http://schoolido.lu/api/events/'

def wikia_crawl():
    for sites in wikia_pages:
        ll = requests.get(wikia_base + sites).content
        ll_soup = bs4.BeautifulSoup(ll, 'html.parser')

        lists = ll_soup.find_all('ol')

        for data_02 in lists:
            for data_03 in data_02:
                if not (data_03 == -1 or data_03 is None):
                    try:
                        for obj in data_03.children:
                            try:
                                if len(obj.string.strip()) > 1 and 'href' in list(obj.attrs.keys()):
                                    try:
                                        links[obj.string] = obj.attrs['href']
                                        swaps[obj.string] = obj.string
                                    except AttributeError:
                                        pass
                                else:
                                    pass
                            except AttributeError:
                                pass
                    except AttributeError:
                        pass


def sif_crawl():
    pass


def test():
    params={'rarity':'UR'}
    cards = requests.get(cache_url).json()
    for item in list(cards['current_event_jp']):
        print(item)

    print(cards['current_event_en']['japanese_name'])
    print(cards['current_event_jp']['japanese_name'])

    params = {'search': cards['current_event_jp']['japanese_name']}
    event = requests.get(event_url, params).json()
    for item in list(event.keys()):
        print(item)

    print(event['results'])


def get_lyrics(title: str, language: str = lyrics_lang[0]):
    title = sub_title(title)
    if title not in links.keys():
        raise ValueError('Sorry, song title was not found!')
    link = links[title]
    link = wikia_base + link
    song = requests.get(link).content
    song_soup = bs4.BeautifulSoup(song, 'html.parser')

    if language is None:
        index = 0
    else:
        index = lyrics_lang.index(language)

    data_01 = song_soup.find_all(class_='poem')
    return title, link, data_01[index].get_text()


def sub_title(title):
    regex = re.compile('.*' + title + '.*', re.IGNORECASE)

    for key in swaps.keys():
        if regex.match(key):
            return swaps[key]


###### SIF ######

def current_event_en():
    cache = requests.get(cache_url).json()
    params = {'search': cache['current_event_en']['japanese_name']}
    event = requests.get(event_url, params).json()
    result = event['results'][0]
    for item in list(result.keys()):
        print(item)


def card(num: int):
    card = requests.get(cards_url + str(num) + '/')
    return card.json()

wikia_crawl()
#current_event_en()
