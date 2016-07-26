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

columns_music = ['code', 'title', 'artist', 'subunit', 'album', 'anime', 'year', 'season', 'category', 'link', 'parent', 'num']
table_music = 'songs'

#playlist stuff
table_playlist = 'playlist'
columns_playlist = ['id', 'name', 'owner', 'song_id']

args = columns_music[:] + ['or']

table_suggest = 'suggestions'
columns_suggest = ['id', 'creator', 'suggestion', 'status', 'change']
status_suggest = ['New', 'Acknowledged', 'Rejected', 'Accepted', 'Finished']


class MusicLinker(object):
    """
    A class to interact with the database of songs.
    """

    def __init__(self, filename):
        self.db = sqlite3.connect(filename)
        self.cursor = self.db.cursor()

    def playlist_name(self, name):
        print(name)
        sql = sql_start + columns_playlist[3] + ' ' + sql_from + table_playlist + ' ' + sql_search + columns_playlist[1] + ' ' + sql_like + sql_param + sql_end
        print(sql)
        results = self.cursor.execute(sql, (name,))
        data = results.fetchone()

        return data

    def playlist_add(self, name, owner, codes):
        data = self.playlist_get(name, owner)[0]

        for code in codes:
            data += ' ' + code

        data = data.strip()
        update = "UPDATE {} SET {} = ? WHERE {} LIKE ? AND {} LIKE ? COLLATE NOCASE".format(table_playlist, columns_playlist[3],
                                                                           columns_playlist[1], columns_playlist[2])

        self.cursor.execute(update, (data, name, owner))
        self.db.commit()

        print(update)

    def playlist_del_song(self, name, owner, num:int):
        data = self.playlist_get(name, owner)[0].split()

        data.pop(num - 1)

        updated = ''
        for code in data:
            updated += code + ' '

        updated = updated.strip()

        update = "UPDATE {} SET {} = ? WHERE {} LIKE ? AND {} LIKE ? COLLATE NOCASE".format(table_playlist, columns_playlist[3],
                                                                         columns_playlist[1], columns_playlist[2])

        self.cursor.execute(update, (updated, name, owner))
        self.db.commit()

        print(update)

    def playlist_del(self, name, owner):
        delete = "DELETE FROM {} WHERE {} IS ? AND {} IS ?".format(table_playlist, columns_playlist[1], columns_playlist[2])

        self.cursor.execute(delete, (name, owner))
        self.db.commit()

    def playlist_get(self, name, owner):
        data = self.playlist_data(name, owner)
        return data

    def playlist_all(self, owner):
        all = "SELECT {} FROM {} WHERE {} IS ? COLLATE NOCASE".format(columns_playlist[1], table_playlist, columns_playlist[2])

        results = self.cursor.execute(all, (owner, ))
        data = results.fetchall()
        return data

    def playlist_data(self, name, owner):
        retrieve = "SELECT {} FROM {} WHERE {} LIKE ? AND {} LIKE ? COLLATE NOCASE".format(columns_playlist[3], table_playlist,
                                                                        columns_playlist[1], columns_playlist[2])
        print(retrieve)
        print(name + ' ' + owner)
        results = self.cursor.execute(retrieve, (name, owner))
        data = results.fetchone()
        return data

    def playlist_create(self, name, owner):
        create = "INSERT INTO {} ({}, {}, {}) VALUES(?,?,?)".format(table_playlist, columns_playlist[1], columns_playlist[2], columns_playlist[3])

        self.cursor.execute(create, (name, owner, ''))
        self.db.commit()

    def playlist_list(self, owner):
        retrieve = "SELECT {} FROM {} WHERE {} IS ?".format(columns_playlist[1], table_playlist, columns_playlist[2])
        results = self.cursor.execute(retrieve, (owner, ))

        data = results.fetchall()
        return data

    def advanced(self, **flags):
        global args
        sql = sql_stemp
        sql += table_music + ' '
        
        values = list()
        flag_or = 0
        flag_remix = 0
        
        if args[len(columns_music)] in flags and flags[args[len(columns_music)]]:
            flag_or = 1

        #Check if args are passed
        if len(list(flags.keys())) > 0:
            sql += sql_search
            
            #SELECT DISTINCT * FROM music WHERE 
            for arg in list(flags.keys()):
                flag_match = 0
                if arg in args[0:len(columns_music)]:
                    #add value to values
                    values.append('%' + flags[arg] + '%')
                
                    sql += columns_music[args.index(arg)] + ' ' + sql_like + sql_param
                    #code, artist, album, link, parent
                    if arg != columns_music[columns_music.index('title')]:
                        flag_remix = 1

                    #add AND or OR
                    if flag_or:
                        sql += sql_or
                    else:
                        sql += sql_and
            
            #replace and/or and add null/not null
            if not flag_remix:        
                if (sql.endswith(sql_or)):
                    sql = sql[:len(sql) - 3] + sql_and
                sql += columns_music[columns_music.index('parent')]
                sql += ' ' + sql_null
            else:
                if (sql.endswith(sql_or)):
                    sql = sql[:len(sql) - 3]
                elif (sql.endswith(sql_and)):
                    sql = sql[:len(sql) - 4]         

        sql += sql_order
        sql += columns_music[0] + ' '

        sql += sql_end

        #print(sql)
        #print(tuple(values))
        
        results = self.cursor.execute(sql, tuple(values))
        data = results.fetchall()
        #print(data)
        return data
        
    def title(self, title=''):
        return self.advanced(title=title)

    def code(self, code=''):
        return self.advanced(code=code)

    def album(self, album=''):
        return self.advanced(album=album)

    def anime(self, anime='', type=''):
        return self.advanced(anime=anime, category=type)

    def albums(self, album):
        print(album)
        sql = 'SELECT DISTINCT album FROM {} WHERE album LIKE ? ORDER BY album COLLATE NOCASE'.format(table_music)
        results = self.cursor.execute(sql, ['%' + album + '%'])
        data = results.fetchall()
        return data

    def suggestion_add(self, creator, suggestion):
        print(creator + ' ' + suggestion)
        sql = 'INSERT INTO {} ({}, {}, {}) VALUES(?,?,?)'.format(table_suggest, columns_suggest[1], columns_suggest[2], columns_suggest[3])
        self.cursor.execute(sql, (creator, suggestion, status_suggest[0]))
        self.db.commit()

    def suggestion_read(self):
        retrieve = 'SELECT {},{},{},{} FROM {} WHERE {} IS ? OR {6} IS ?'.format(columns_suggest[0], columns_suggest[1], columns_suggest[2], columns_suggest[3], table_suggest, columns_suggest[3], columns_suggest[3])
        data = self.cursor.execute(retrieve, (status_suggest[0], status_suggest[1]))
        print(retrieve)
        rows = data.fetchall()
        update = 'UPDATE {} SET {} = ? WHERE {} = ?'.format(table_suggest, columns_suggest[3], columns_suggest[3])
        self.cursor.execute(update, (status_suggest[1], status_suggest[0]))
        self.db.commit()


        return rows

    def suggestion_status(self, id: int):
        retrieve = 'SELECT {},{} FROM {} WHERE {} IS ?'.format(columns_suggest[2], columns_suggest[3], table_suggest, columns_suggest[1])
        data = self.cursor.execute(retrieve, (id,))

        return data.fetchall()

    def suggestion_reject(self, id: int, reason: str):
        reject = 'UPDATE {} SET {} = ?, {} = ? WHERE {} IS ?'.format(table_suggest, columns_suggest[3], columns_suggest[4], columns_suggest[0])
        self.cursor.execute(reject, (status_suggest[2], reason, id))
        self.db.commit()

        get_id = 'SELECT {},{},{} FROM {} WHERE {} IS ?'.format(columns_suggest[1], columns_suggest[2], columns_suggest[4], table_suggest, columns_suggest[0])
        data = self.cursor.execute(get_id, (id,))
        return data.fetchone()

    def suggestion_accept(self, id: int, reason: str):
        accept = 'UPDATE {} SET {} = ?, {} = ? WHERE {} IS ?'.format(table_suggest, columns_suggest[3],
                                                                         columns_suggest[4], columns_suggest[0])
        self.cursor.execute(accept, (status_suggest[3], reason, id))
        self.db.commit()

        get_id = 'SELECT {},{},{} FROM {} WHERE {} IS ?'.format(columns_suggest[1], columns_suggest[2],
                                                                     columns_suggest[4], table_suggest,
                                                                     columns_suggest[0])
        data = self.cursor.execute(get_id, (id,))
        return data.fetchone()

    def suggestion_accepted(self):
        retrieve = 'SELECT {},{},{},{} FROM {} WHERE {} IS ?'.format(columns_suggest[0],
                                                                                       columns_suggest[1],
                                                                                       columns_suggest[2],
                                                                                       columns_suggest[3],
                                                                                       table_suggest,
                                                                                       columns_suggest[3])
        data = self.cursor.execute(retrieve, (status_suggest[3],))
        print(retrieve)
        rows = data.fetchall()

        return rows

    def suggestion_finish(self, id: int, reason: str):
        accept = 'UPDATE {} SET {} = ?, {} = ? WHERE {} IS ?'.format(table_suggest, columns_suggest[3],
                                                                         columns_suggest[4], columns_suggest[0])
        self.cursor.execute(accept, (status_suggest[4], reason, id))
        self.db.commit()

        get_id = 'SELECT {},{},{} FROM {} WHERE {} IS ?'.format(columns_suggest[1], columns_suggest[2],
                                                                     columns_suggest[4], table_suggest,
                                                                     columns_suggest[0])
        data = self.cursor.execute(get_id, (id,))
        return data.fetchone()

