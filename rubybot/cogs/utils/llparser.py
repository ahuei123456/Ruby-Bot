import requests
import bs4
import re
import datetime
from datetime import timezone
from datetime import timedelta
from copy import deepcopy
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

ss_anime_start = datetime.datetime(2016, 7, 2, 22, 30, 0, 0, timezone(timedelta(hours=9), name='JST'))
ss_phrases = (
    'We want to shine!',
)

ss_subs = (
    ('FFFansubs', 'http://fffansubs.org/'),
    ('動畫瘋 (TW)', 'http://ani.gamer.com.tw/index.php'),
    ('LiTV (TW)', 'https://www.litv.tv/vod/comic'),
    ('Viu.com (HK)', 'https://www.viu.com'),
    ('ANIPLUS (KR)', 'http://www.aniplustv.com/ip.asp#/tv/program_view.asp?gCode=TV&sCode=010&contentSerial=1755'),
    ('DEX (TH)', 'http://www.dexchannel.com'),
    ('MADMAN (Oceania)', 'http://www.animelab.com'),
    ('Anime Limited (France)', 'http://www.wakanim.tv'),
    ('Anime Limited (UK/Republic of Ireland/Isle of Man)', 'http://www.crunchyroll.com'),
    ('AV Visionen (Germany/Austria/Switzerland/Luxembourg/Liechtenstein)', 'http://www.anime-on-demand.de'),
    ('Funimation (US/Canada)', 'http://www.funimation.com/videos/simulcasts_shows')
)

ss_raws = (
    ('LINE Live', 'https://live.line.me/r/channels/91/upcoming/6886'),
    ('Bandai Channel', 'http://live.b-ch.com/lovelive_anime'),
    ('Animate Channel', 'http://www.animatechannel.com/live/lovelive_anime'),
    ('Niconico Live (JP)', 'http://live.nicovideo.jp/gate/lv267944319'),
    ('AbemaTV (JP)', 'https://abema.tv/')
)

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
    # http://schoolido.lu/api/events/?ordering=-english_beginning&page_size=1
    params = {'ordering': '-english_beginning', 'page_size': 1}
    events = requests.get(event_url, params=params).json()
    event = events['results'][0]

    en_start = convert_time(event['english_beginning'])
    en_end = convert_time(event['english_end'])

    event['en_start'] = encode_time(en_start)
    event['en_end'] = encode_time(en_end)
    event['en_time'] = event_remaining(en_start, en_end)
    return event


def current_event_jp():
    params = {'ordering': '-beginning', 'page_size': 1}
    events = requests.get(event_url, params=params).json()
    event = events['results'][0]

    jp_start = convert_time(event['beginning'])
    jp_end = convert_time(event['end'])

    event['jp_start'] = encode_time(jp_start)
    event['jp_end'] = encode_time(jp_end)
    event['jp_time'] = event_remaining(jp_start, jp_end)
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

###### Sunshine ######


def get_next_ep():
    now = datetime.datetime.now(timezone.utc)
    next_ep = deepcopy(ss_anime_start)
    diff = next_ep - now
    ep_num = 1

    while diff.total_seconds() < 0:
        ep_num += 1
        next_ep = next_ep + timedelta(weeks=1)

    msg = encode_next_ep(ep_num, diff, next_ep)
    msg += '\n\n' + encode_raws() + '\n\n' + encode_subs()
    return msg


def encode_next_ep(ep_num, diff, airtime):
    seconds = diff.seconds

    hours = seconds // 3600
    seconds -= hours * 3600

    minutes = seconds // 60
    seconds -= minutes * 60

    airing = False
    if diff.days == 6 and hours == 23 and minutes > 30:
        airing = True
    msg = '**Love Live! Sunshine!! TV Anime**\n'
    if airing:
        msg += '**Current Episode: Episode {}\n'.format(ep_num - 1)
        msg += '**Currently airing!**'
    else:
        msg += '**Next Episode**: Episode {}\n'.format(ep_num)
        msg += '**Airing in**: {} days, {} hours, {} minutes and {} seconds\n'.format(diff.days, hours, minutes,
                                                                                      seconds)
        msg += '**Airing on**: ' + airtime.strftime('%B %d, %Y %H:%M:%S %Z') + '\n'

    msg += '**{}**'.format(ss_phrases[0])
    return msg


def encode_raws():
    msg = '**Raw Sources**\n'

    for item in ss_raws:
        msg += '**' + item[0] + '**: <' + item[1] + '>\n'

    msg = msg.strip()
    return msg


def encode_subs():
    msg = '**Subtitled Sources** (1 hr delay after raws)\n'

    for item in ss_subs:
        msg += '**' + item[0] + '**: <' + item[1] + '>\n'

    msg = msg.strip()
    return msg


wikia_crawl()
#current_event_en()
