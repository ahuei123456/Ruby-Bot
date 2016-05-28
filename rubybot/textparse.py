import dbconn
import random

from dbconn import MusicLinker

args = ['-id', '-t', '-ar', '-su', '-al', '-an', '-yr', '-ss', '-st', '-ln', '-rm', '-tn', '-or', '-c', '-rr', '-rn']

index_or = args.index('-or')
index_count = args.index('-c')
index_rr = args.index('-rr')
index_rn = args.index('-rn')


def title(data):
    if len(data) < 1:
        data.append('')
    return music.title(data[0])


def code(data):
    return music.code(data)


def album(data):
    return music.album(data[0])


def albums(data):
    return music.albums(data[0])


def anime(data, type=''):
    return music.anime(data[0], type)


def adv(data):
    print(data)
    fdata = dict()
    saved_flag = ''
    count = 1
    flag_random = 0
    flag_repeat = 0
    for x in range(0, len(data)):
        if x == 0 and data[x] not in args:
            fdata[dbconn.columns[2]] = data[0]

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


def fix_input(raw, special = args):
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

music = MusicLinker('files\music.db')
