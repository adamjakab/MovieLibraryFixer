import sqlite3
import os
import json
from moviefixer.logger import log, log_debug

class MovieLibrary:
    __db = None
    __db_file = None
    __db_table_name = "movie"
    __db_table = None
    
    def __init__(self, db_file):
        self.__db_file = db_file
        self.initDatabase()
        self.__db = sqlite3.connect(self.__db_file)
        self.__db.row_factory = self.__dict_factory
        
        log("Ready(%s).", db_file)
        log_debug("Item count: %s", self.countAllItems())
        
        # connection.close()
    
    def registerMovieData(self, d):
        if (d != None):
            if(self.findItemById(d['id'])):
                log_debug("DB(update)> %s", d['id'])
                cur = self.__db.cursor()
                cur.execute("UPDATE movie SET path = ?,  title = ?, bit_rate = ?, duration = ?, format_name = ?, format_long_name = ?, size = ?, streams = ? WHERE id = ?", 
                            (d['path'], d['title'], d['bit_rate'], d['duration'], d['format_name'], d['format_long_name'], d['size'], json.dumps(d['streams']), d['id'])
                            )
            else:
                log_debug("DB(insert)> %s", d['id'])
                cur = self.__db.cursor()                
                sql = "INSERT INTO movie (id, path, title, bit_rate, duration, format_name, format_long_name, size, streams) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
                cur.execute(sql, (d['id'], d['path'], d['title'], d['bit_rate'], d['duration'], d['format_name'], d['format_long_name'], d['size'], json.dumps(d['streams'])))
                
            self.__db.commit()
        else:
            raise Exception("Invalid data for database!", d)
        
    def deleteItemById(self, _id):
        log_debug("DB(delete)>: %s", _id)
        cur = self.__db.cursor()
        cur.execute("DELETE FROM movie WHERE id = :id", {"id": _id})
        self.__db.commit()
    
    
    def findItemByPath(self, path):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM movie WHERE path = :path", {"path": path})
        return cur.fetchone()
    
    def findItemById(self, _id):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM movie WHERE id = :id", {"id": _id})
        return cur.fetchone()

    def countAllItems(self):
        return len(self.getAllItems())
    
    def getAllItems(self):
        cur = self.__db.cursor()
        cur.execute("SELECT * FROM movie")
        return cur.fetchall()
    
    # Converts answer into dict and creates dict for streams
    def __dict_factory(self, cur, row):
        d = {}
        for idx, col in enumerate(cur.description):
            #log_debug("RF(col|val): %s | %s", col[0], row[idx])
            if(col[0] == "streams"):
                d[col[0]] = json.loads(row[idx])
            else:
                d[col[0]] = row[idx]
        return d
    
    def initDatabase(self):
        if(os.path.isfile(self.__db_file) is False):
            sql = "CREATE TABLE movie("
            sql = sql + "{name} {type}, ".format(name="id", type="text")
            sql = sql + "{name} {type}, ".format(name="path", type="text")
            sql = sql + "{name} {type}, ".format(name="title", type="text")
            sql = sql + "{name} {type}, ".format(name="bit_rate", type="integer")
            sql = sql + "{name} {type}, ".format(name="duration", type="integer")
            sql = sql + "{name} {type}, ".format(name="format_name", type="text")
            sql = sql + "{name} {type}, ".format(name="format_long_name", type="text")
            sql = sql + "{name} {type}, ".format(name="size", type="integer")
            sql = sql + "{name} {type} ".format(name="streams", type="text")
            sql = sql + ")"
            con = sqlite3.connect(self.__db_file)
            cur = con.cursor()
            cur.execute(sql)
            cur.execute('CREATE UNIQUE INDEX "i_id" ON "movie" ("id" ASC)')
            cur.execute('CREATE UNIQUE INDEX "i_path" ON "movie" ("path" ASC)')
            con.commit()
            con.close()
            
