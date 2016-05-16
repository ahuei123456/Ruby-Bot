import sqlite3

sql_start = 'SELECT DISTINCT '
sql_stemp = 'SELECT DISTINCT * FROM '
sql_param = '? '
sql_from = 'FROM '
sql_search = 'WHERE '
sql_like = 'LIKE '
sql_null = 'IS NULL '
sql_notnull = 'IS NOT NULL '
sql_order = 'ORDER BY '
sql_asc = 'ASC '
sql_end = 'COLLATE NOCASE'
sql_and = 'AND '
sql_or = 'OR '

columns = ['code', 'title', 'artist', 'album', 'link', 'parent', 'num']
music_table = 'music'

#playlist stuff
playlist_table = 'playlist'
p_columns = ['id', 'name', 'owner', 'song_id']

#-id id, -t title, -a artist, -al album, -ln link, -rm parent (gib id), -tn track number
#args = ['-id', '-t', '-a', '-al', '-ln', '-rm', '-tn', '-or']
args = columns[:] + ['or']

class MusicLinker(object):
    """
    A class to interact with the database of songs.
    """

    def __init__(self, filename):
        self.db = sqlite3.connect(filename)
        self.cursor = self.db.cursor()

    def playlist_name(self, name):
        print(name)
        sql = sql_start + p_columns[3] + ' ' + sql_from + playlist_table + ' ' + sql_search + p_columns[1] + ' ' + sql_like + sql_param + sql_end
        print(sql)
        results = self.cursor.execute(sql, (name,))
        data = results.fetchone()

        return data

    def advanced(self, **flags):
        global args
        sql = sql_stemp
        sql += music_table +  ' '
        
        values = list()
        flag_or = 0
        flag_remix = 0
        
        if args[7] in flags and flags[args[7]]:
            flag_or = 1

        #Check if args are passed
        if len(list(flags.keys())) > 0:
            sql += sql_search
            
            #SELECT DISTINCT * FROM music WHERE 
            for arg in list(flags.keys()):
                flag_match = 0
                if arg in args[0:7]:
                    #add value to values
                    values.append('%' + flags[arg] + '%')
                
                    sql += columns[args.index(arg)] + ' ' + sql_like + sql_param
                    #code, artist, album, link, parent
                    if arg == args[0] or arg == args[2] or arg == args[3] or arg == args[4] or arg == args[5]:
                        flag_remix = 1

                    #add AND or OR
                    if flag_or:
                        sql += sql_or
                    else:
                        sql += sql_and
            #replace and/or and add null/not null
            if flag_or:        
                if (sql.endswith(sql_or)):
                    sql = sql[:len(sql) - 3] + sql_and
                sql += columns[5]
                sql += ' ' + sql_null
            else:
                if (sql.endswith(sql_or)):
                    sql = sql[:len(sql) - 3]
                elif (sql.endswith(sql_and)):
                    sql = sql[:len(sql) - 4]         

        sql += sql_order
        sql += columns[0] + ' '

        sql += sql_end

        print(sql)
        print(tuple(values))
        
        results = self.cursor.execute(sql, tuple(values))
        data = results.fetchall()
        print(data)
        return data
        
    def title(self, title):
        return self.advanced(title = title)

    def code(self, code):
        return self.advanced(code = code)

    def album(self, album):
        return self.advanced(album = album)

test = MusicLinker('files\music.db')
test.advanced(title='bokura', artist='nico')
test.album('umiiro')
