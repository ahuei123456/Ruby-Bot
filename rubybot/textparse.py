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

music = MusicLinker('files\music.db')
