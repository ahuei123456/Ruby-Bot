from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import json
import requests


EN = 0
ROMAJI = 1
KANJI = 2
BASE_URL = r'https://fsc9cff890.execute-api.us-east-1.amazonaws.com/test/songs/'

songs = None
titles = None
song_info = dict()


def update_cache():
    global songs
    global titles

    response = requests.get(BASE_URL)
    if response.status_code == requests.codes.ok:
        songs = response.json()
        titles = dict()

        for index, song in enumerate(songs):
            titles[song['title']['romaji']] = index


def update_song_info_cache(title):
    global song_info

    response = requests.get(BASE_URL, {'title': title})
    if response.status_code == requests.codes.ok:
        song_info[title] = response.json()


def get_songs(artist=None):
    if songs is None:
        update_cache()

    if artist is not None:
        artist = artist.lower()
        songs = [song for song in songs if song['artist'].lower() == artist]

    return songs


def get_artists():
    if songs is None:
        update_cache()

    artists = {song['artist'] for song in songs}
    return artists


def get_lyrics(title, lang=EN):
    if titles is None:
        update_cache()

    cached_titles = list(titles.keys())
    result = process.extractOne(title, cached_titles, score_cutoff=75)
    
    if result is None:
        update_cache()
        cached_titles = titles.keys()
        result = process.extractOne(title, cached_titles, score_cutoff=75)
        if result is None:
            return None

    title = result[0]
    id = titles[title]
    song = songs[id]
    arg = song['str_id']

    if arg not in song_info:
        update_song_info_cache(arg)

    song_data = song_info[arg]
    
    if lang == EN:
        return song_data['lyrics']['en']
    elif lang == ROMAJI:
        return song_data['lyrics']['romaji']
    else:
        return None