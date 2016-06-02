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

columns = ['code', 'title', 'artist', 'subunit', 'album', 'anime', 'year', 'season', 'category', 'link', 'parent', 'num']
table_music = 'songs'

#playlist stuff
playlist_table = 'playlist'
p_columns = ['id', 'name', 'owner', 'song_id']

args = columns[:] + ['or']

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
        sql = sql_start + p_columns[3] + ' ' + sql_from + playlist_table + ' ' + sql_search + p_columns[1] + ' ' + sql_like + sql_param + sql_end
        print(sql)
        results = self.cursor.execute(sql, (name,))
        data = results.fetchone()

        return data

    def advanced(self, **flags):
        global args
        sql = sql_stemp
        sql += table_music + ' '
        
        values = list()
        flag_or = 0
        flag_remix = 0
        
        if args[len(columns)] in flags and flags[args[len(columns)]]:
            flag_or = 1

        #Check if args are passed
        if len(list(flags.keys())) > 0:
            sql += sql_search
            
            #SELECT DISTINCT * FROM music WHERE 
            for arg in list(flags.keys()):
                flag_match = 0
                if arg in args[0:len(columns)]:
                    #add value to values
                    values.append('%' + flags[arg] + '%')
                
                    sql += columns[args.index(arg)] + ' ' + sql_like + sql_param
                    #code, artist, album, link, parent
                    if arg != columns[columns.index('title')]:
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
                sql += columns[columns.index('parent')]
                sql += ' ' + sql_null
            else:
                if (sql.endswith(sql_or)):
                    sql = sql[:len(sql) - 3]
                elif (sql.endswith(sql_and)):
                    sql = sql[:len(sql) - 4]         

        sql += sql_order
        sql += columns[0] + ' '

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
        sql = 'SELECT DISTINCT album FROM music WHERE album LIKE ? ORDER BY album COLLATE NOCASE'
        results = self.cursor.execute(sql, ['%' + album + '%'])
        data = results.fetchall()
        return data

    def suggestion_add(self, creator, suggestion):
        print(creator + ' ' + suggestion)
        sql = 'INSERT INTO {0} ({1}, {2}, {3}) VALUES(?,?,?)'.format(table_suggest, columns_suggest[1], columns_suggest[2], columns_suggest[3])
        self.cursor.execute(sql, (creator, suggestion, status_suggest[0]))
        self.db.commit()

    def suggestion_read(self):
        retrieve = 'SELECT {0},{1},{2},{3} FROM {4} WHERE {5} IS ? OR {6} IS ?'.format(columns_suggest[0], columns_suggest[1], columns_suggest[2], columns_suggest[3], table_suggest, columns_suggest[3], columns_suggest[3])
        data = self.cursor.execute(retrieve, (status_suggest[0], status_suggest[1]))
        print(retrieve)
        rows = data.fetchall()
        update = 'UPDATE {0} SET {1} = ? WHERE {2} = ?'.format(table_suggest, columns_suggest[3], columns_suggest[3])
        self.cursor.execute(update, (status_suggest[1], status_suggest[0]))
        self.db.commit()


        return rows

    def suggestion_status(self, id: int):
        retrieve = 'SELECT {0},{1} FROM {2} WHERE {3} IS ?'.format(columns_suggest[2], columns_suggest[3], table_suggest, columns_suggest[1])
        data = self.cursor.execute(retrieve, (id,))

        return data.fetchall()

    def suggestion_reject(self, id: int, reason: str):
        reject = 'UPDATE {0} SET {1} = ?, {2} = ? WHERE {3} IS ?'.format(table_suggest, columns_suggest[3], columns_suggest[4], columns_suggest[0])
        self.cursor.execute(reject, (status_suggest[2], reason, id))
        self.db.commit()

        get_id = 'SELECT {0},{1},{2} FROM {3} WHERE {4} IS ?'.format(columns_suggest[1], columns_suggest[2], columns_suggest[4], table_suggest, columns_suggest[0])
        data = self.cursor.execute(get_id, (id,))
        return data.fetchone()

    def suggestion_accept(self, id: int, reason: str):
        accept = 'UPDATE {0} SET {1} = ?, {2} = ? WHERE {3} IS ?'.format(table_suggest, columns_suggest[3],
                                                                         columns_suggest[4], columns_suggest[0])
        self.cursor.execute(accept, (status_suggest[3], reason, id))
        self.db.commit()

        get_id = 'SELECT {0},{1},{2} FROM {3} WHERE {4} IS ?'.format(columns_suggest[1], columns_suggest[2],
                                                                     columns_suggest[4], table_suggest,
                                                                     columns_suggest[0])
        data = self.cursor.execute(get_id, (id,))
        return data.fetchone()

    def suggestion_accepted(self):
        retrieve = 'SELECT {0},{1},{2},{3} FROM {4} WHERE {5} IS ?'.format(columns_suggest[0],
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
        accept = 'UPDATE {0} SET {1} = ?, {2} = ? WHERE {3} IS ?'.format(table_suggest, columns_suggest[3],
                                                                         columns_suggest[4], columns_suggest[0])
        self.cursor.execute(accept, (status_suggest[4], reason, id))
        self.db.commit()

        get_id = 'SELECT {0},{1},{2} FROM {3} WHERE {4} IS ?'.format(columns_suggest[1], columns_suggest[2],
                                                                     columns_suggest[4], table_suggest,
                                                                     columns_suggest[0])
        data = self.cursor.execute(get_id, (id,))
        return data.fetchone()

