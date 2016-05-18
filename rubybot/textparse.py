import dbconn

from dbconn import MusicLinker

args = ['-id', '-t', '-a', '-al', '-ln', '-rm', '-tn', '-or', '-c', '-rr', '-rn']

def title(data):
    return music.title(data[0])

def code(data):
    return music.code(data[0])

def album(data):
    return music.album(data[0])

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
            if args.index(data[x]) >= 8:
                if data[x] == args[8]:
                    count = int(data[x])
                elif data[x] == args[9]:
                    flag_random = 1
                    flag_repeat = 1
                elif data[x] == args[10]:
                    flag_random = 1

            else:
                saved_flag = data[x]
            print(saved_flag)

        else:
            if saved_flag != '':
                fdata[dbconn.args[args.index(saved_flag)]] = data[x]
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
            if len(fpick > 0):
                play.append(fpick.pop(random.randrange(len(fpick))))
            else:
                break

    return play

def fix_input(raw):
    text = raw.split()
    output = []
    build = ''
    for x in range(0, len(text)):
        string = text[x]
        
        if string in args:
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
                build += string[:len(string) - 1]
                output.append(build.strip())
                build = ''
            else:
                build += ' ' + string
                
        
    if len(build) > 0:
        output.append(build.strip().rstrip())

    
    return output

music = MusicLinker('files\music.db')
