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
    for x in range(0, len(data)):
        pass

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
