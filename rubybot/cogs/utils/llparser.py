import requests
import bs4
import re
import datetime
from datetime import timezone
from datetime import timedelta
import json

day = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
month = ('Dummy', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
time_format = "%a %b %d %Y %H:%M:%S %Z"

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
songs_url = 'http://schoolido.lu/api/songs/'

info_song = [
    "**Title**: {name}",
    "**Title (Romaji)**: {romaji_name}",
    "**Title (English)**: {translated_name}",
    "**Attribute**: {attribute}",
    "**BPM**: {BPM}",
    "**Time (seconds)**: {time}",
    "**Difficulty (Easy)**: {easy_difficulty}",
    "**Notes (Easy)**: {easy_notes}",
    "**Difficulty (Normal)**: {normal_difficulty}",
    "**Notes (Normal)**: {normal_notes}",
    "**Difficulty (Hard)**: {hard_difficulty}",
    "**Notes (Hard)**: {hard_notes}",
    "**Difficulty (Expert)**: {expert_difficulty}",
    "**Difficulty (EXR)**: {expert_random_difficulty}",
    "**Notes (Expert)**: {expert_notes}",
    "**Image**: {image}"
]

info_event_jp = [
    "**Title**: {japanese_name}",
    "**Title (Romaji)**: {romaji_name}",
    "**Start**: {jp_start}",
    "**End**: {jp_end}",
    "**Current event**: {japan_current}",
    "**T1 points**: {japanese_t1_points}",
    "**T1 rank**: {japanese_t1_rank}",
    "**T2 points**: {japanese_t2_points}",
    "**T2 rank**: {japanese_t2_rank}",
    "**Note**: {note}",
    "**Banner**: {image}"
]

info_event_en = [
    "**Title (English)**: {english_name}",
    "**Start**: {en_start}",
    "**End**: {en_end}",
    "**Current event**: {world_current}",
    "**T1 points**: {english_t1_points}",
    "**T1 rank**: {english_t1_rank}",
    "**T2 points**: {english_t2_points}",
    "**T2 rank**: {english_t2_rank}",
    "**Note**: {note}",
    "**Banner**: {english_image}"
]

info_current_jp =[
    "**Event JP**: {japanese_name}",
    "**START**: {jp_start}",
    "**END**: {jp_end}",
    "{jp_time}",
    "{image}"
]

info_current_en =[
    "**Event EN**: {english_name}",
    "**START**: {en_start}",
    "**END**: {en_end}",
    "{en_time}",
    "{english_image}"
]

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
    event = get_event_en(cache['current_event_en']['japanese_name'])
    return event


def current_event_jp():
    cache = requests.get(cache_url).json()
    event = get_event_jp(cache['current_event_jp']['japanese_name'])
    return event


def get_card(num: int):
    card = requests.get(cards_url + str(num) + '/')
    return card.json()


def get_song(title: str):
    params = {'search': title}
    song = requests.get(songs_url, params=params).json()
    return song['results'][0]


def get_event_jp(title: str):
    params = {'search': title}
    events = requests.get(event_url, params=params).json()
    event = events['results'][0]

    jp_start = convert_time(event['beginning'])
    jp_end = convert_time(event['end'])

    event['jp_start'] = encode_time(jp_start)
    event['jp_end'] = encode_time(jp_end)
    event['jp_time'] = event_remaining(jp_start, jp_end)
    return event


def get_event_en(title: str):
    params = {'search': title}
    events = requests.get(event_url, params=params).json()
    event = events['results'][0]

    en_start = convert_time(event['english_beginning'])
    en_end = convert_time(event['english_end'])

    event['en_start'] = encode_time(en_start)
    event['en_end'] = encode_time(en_end)
    event['en_time'] = event_remaining(en_start, en_end)
    return event


def encode_card(card):
    pass


def encode_event_en(event):
    return encode_info(info_event_en, event)


def encode_event_jp(event):
    return encode_info(info_event_jp, event)


def encode_current_en(event):
    return encode_info(info_current_en, event)


def encode_current_jp(event):
    return encode_info(info_current_jp, event)


def encode_song(song):
    return encode_info(info_song, song)


def encode_info(info_text, data):
    info = ''

    for label in info_text:
        try:
            line = label.format(**data) + '\n'
            info += line
        except AttributeError:
            pass

    return info


def convert_time(time):
    # 2014-11-05T09:00:00Z
    # yyyy-mm-ddThh:mm:ssZ
    # 2013-06-12T16:00:00+09:00
    if time is None:
        return None
    if len(time) < 10:
        return None

    year = int(time[:4])
    month = int(time[5:7])
    date = int(time[8:10])

    hour = int(time[11:13])
    minute = int(time[14:16])
    second = int(time[17:19])

    if len(time) > 21:
        tz = timezone(timedelta(hours=9))
    else:
        tz = timezone.utc

    dt = datetime.datetime(year, month, date, hour, minute, second, 0, tz)
    return dt


def encode_time(dt):
    if dt is None:
        return None
    dt_str = dt.strftime(time_format)
    return dt_str


def event_remaining(dt_start, dt_end):
    now = datetime.datetime.now(timezone.utc)

    diff_end = dt_end - now
    diff_start = now - dt_start
    if diff_start.total_seconds() < 0:
        return "Event has not started yet!"
    elif diff_end.total_seconds() < 0:
        return "Event has ended!"
    else:
        seconds = diff_end.seconds

        hours = seconds // 3600
        seconds -= hours * 3600

        minutes = seconds // 60
        seconds -= minutes * 60

        return "Event ends in {} days, {} hours, {} minutes and {} seconds.".format(diff_end.days, hours, minutes, seconds)

wikia_crawl()
#current_event_en()
