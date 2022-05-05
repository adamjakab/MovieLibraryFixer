import os
from tinydb import TinyDB, Query, where
#from tinydb.storages import JSONStorage

from moviefixer.logger import log, log_debug

class MovieLibrary:
    __db = None
    __db_file = None
    __db_table_name = "movie"
    __db_table = None

    def __init__(self, db_file):
        self.__db_file = db_file
        self.__db = TinyDB(self.__db_file)
        self.__db_table = self.__createTable(self.__db_table_name)
        log("Ready(%s).", db_file)
        log_debug("Item count: %s", self.countAllItems()) 

    def getAllItems(self):
        return self.__db_table.all()
    
    def countAllItems(self):
        return len(self.getAllItems())

    def findItemByHeight(self, height):
        #log_debug("Looking for Height: %s", height)
        answer = self.__db_table.search(where('height') > height)
        return answer

    def findItemById(self, id):
        #log_debug("Looking for ID: %s", id)
        answer = self.__db_table.search(where('id') == id)
        return answer

    def findItemByPath(self, path):
        #self.log_debug("Looking for Path: %s", path)
        answer = self.__db_table.search(where('path') == path)
        return answer

    def registerMovieData(self, d):
        if (d != None):
            log_debug("DB(upsert)> %s", d['id'])
            q = Query()
            self.__db_table.upsert(d, q.id == d['id'])
        else:
            raise Exception("Invalid data for database!", d)
        
    def deleteItemById(self, id):
        log_debug("DB(delete)>: %s", id)
        self.__db_table.remove(where('id') == id)
    
    def __createTable(self, tableName):
        table = self.__db.table(tableName)
        return table
