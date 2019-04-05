import random
import os
import json

from cogs.utils import dbconn
from cogs.utils.dbconn import MusicLinker

args_full = ['-id', '-t', '-ar', '-su', '-al', '-an', '-yr', '-ss', '-st', '-ln', '-rm', '-tn', '-or', '-c', '-rr', '-rn']

index_or = args_full.index('-or')
index_count = args_full.index('-c')
index_rr = args_full.index('-rr')
index_rn = args_full.index('-rn')


def title(data):
    if len(data) < 1:
        data.append('')
    return music.title(data)


def code(data):
    return music.code(data)


def album(data):
    return music.album(data)


def albums(data):
    return music.albums(data)


def anime(data, type=''):
    return music.anime(data, type)


def adv(data, args=args_full):
    print(data)
    fdata = dict()
    saved_flag = ''
    count = 1
    flag_random = 0
    flag_repeat = 0
    for x in range(0, len(data)):
        if x == 0 and data[x] not in args:
            fdata[dbconn.columns_music[2]] = data[0]

        elif data[x] in args:
            if args.index(data[x]) >= index_or:
                if data[x] == args[index_or]:
                    print('-or')
                    saved_flag = data[x]
                elif data[x] == args[index_rr]:
                    print('-rr')
                    flag_random = 1
                    flag_repeat = 1
                elif data[x] == args[index_rn]:
                    print('-c')
                    flag_random = 1

            else:
                saved_flag = data[x]
            print(saved_flag)

        else:
            if saved_flag != '':
                if args.index(saved_flag) <= index_or:
                    fdata[dbconn.args[args.index(saved_flag)]] = data[x]
                else:
                    count = int(data[x])
                saved_flag = ''
    print(fdata)
    output = music.advanced(**fdata)

    if flag_random:
        output = randomize(output, flag_repeat, count)
    return output


def randomize(rlist, repeat = 0, count = 1):
    fpick = rlist[:]
    play = list()

    if count == -1:
        count = len(fpick)

    for x in range(0, count):
        if repeat:
            play.append(fpick[random.randrange(len(fpick))])
        else:
            if len(fpick) > 0:
                play.append(fpick.pop(random.randrange(len(fpick))))
            else:
                break

    return play


def get_playlist_songs(name, owner):
    code_str = get_playlist(name, owner)[0]
    code_list = code_str.split()

    links = list()
    for code_song in code_list:
        links.append(code(code_song)[0])

    return links


def get_playlist(name, owner):
    playlist = music.playlist_get(name, str(owner.id))
    if playlist is None:
        raise ValueError('No playlist found!')
    return playlist

def get_playlist_list(owner):
    playlists = music.playlist_list(owner.id)
    if playlists is None or len(playlists) == 0:
        raise ValueError('You do not have any playlists!')
    return playlists


def del_from_playlist(name, owner, num:int):
    music.playlist_del_song(name, owner.id, num)


def del_playlist(name, owner):
    music.playlist_del(name, owner.id)


def add_song_to_playlist(name, owner, code):
    music.playlist_add(name, owner.id, code)


def create_playlist(name, owner):
    music.playlist_create(name, owner.id)


def fix_input(raw, special=args_full):
    if special is None:
        special = list()
    text = raw.split()
    output = []
    build = ''
    for x in range(0, len(text)):
        string = text[x]
        
        if string in special:
            build = build.strip()
            if (len(build) > 0):
                output.append(build)
            output.append(string)
            build = ''
        elif len(build) == 0:
            if not string.startswith('"'):
                build += string
            else:
                # "food"
                if string.endswith('"'):
                    output.append(string[1:len(string) - 1])
                else:
                    build += ' ' + string[1:]
        else:
            if string.endswith('"'):
                build += ' ' + string[:len(string) - 1]
                output.append(build.strip())
                build = ''
            else:
                build += ' ' + string
                
        
    if len(build) > 0:
        output.append(build.strip().rstrip())

    if len(output) > 150:
        output = output[:151]
    return output


def suggest(creator: int, suggestion: str):
    music.suggestion_add(creator, suggestion)


def read():
    return music.suggestion_read()


def reject(id: int, reason: str):
    return music.suggestion_reject(id, reason)


def accept(id: int, reason: str):
    return music.suggestion_accept(id, reason)


def accepted():
    return music.suggestion_accepted()


def finish(id: int, reason: str):
    return music.suggestion_finish(id, reason)


def load_credentials():
    path = os.path.join(os.getcwd(), 'files', 'credentials.json')
    with open(path) as f:
        return json.load(f)

def addsong(rawinfo):
    info = list()
    for i in range(0, len(rawinfo)):
        if rawinfo[i] == '*':
            print(True)
            info.append(None)
        else:
            info.append(rawinfo[i])

    while len(info) < 12:
        info.append(None)

    try:
        info[len(info) - 1] = int(info)
    except Exception:
        pass

    music.addsong(info)


def load_list():
    path = os.path.join(os.getcwd(), 'files', 'credentials.json')
    with open(path, 'r+') as f:
        data = json.load(f)

        f.seek(0)  # <--- should reset file position to the beginning.
        json.dump(data, f, indent=4)


def is_dm(msg):
    server = msg.server
    if not server:
        return True
    return False


music = MusicLinker(os.path.join('files', 'music.db'))
