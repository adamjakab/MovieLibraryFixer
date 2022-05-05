'''
Created on 23 Apr 2022

@author: jackisback
'''
import glob
import os
import json
from moviefixer.task import Task
from moviefixer.movieitem import MovieItem
from moviefixer.logger import log, log_debug, log_info, log_warn, log_error

class ScanLibraryTask(Task):
    __library_folders = []
    __all_movie_extensions = ['.avi', '.divx', '.m4v', '.mkv', '.mp4']
    __non_mkv_movie_extensions = ['.avi', '.divx', '.m4v', '.mp4']

    def __init__(self, library):
        super(ScanLibraryTask, self).__init__(library)
        
        
    def configure(self, params):
        self.__config = params
        
        if("folders" in self.__config and len(self.__config["folders"]) > 0):
            for folder in self.__config["folders"]:
                if(os.path.isdir(folder) is False):
                    raise Exception("Bad library path supplied!", folder)
                else:
                    log("Added library path: %s", folder)
        else:
            raise Exception("No usable library paths!")
        
        self.__library_folders = self.__config["folders"]
        self.__config["update_existing"] = "update_existing" in self.__config and self.__config["update_existing"] == True
        self.__config["remove_deleted"] = "remove_deleted" in self.__config and self.__config["remove_deleted"] == True
        
        log_debug("Configured: %s", json.dumps(self.__config)) 

    def run(self):
        log("Running...")        
        self.__run_update__()
        self.__run_remove__()
        log("Done.")


    def __run_remove__(self):
        if(self.__config["remove_deleted"] == False):
            log_debug("Library cleanup from deleted item is disabled. Skipping")
            return
           
        library = self.getLibrary()
        movieDataItems = library.getAllItems()
        for md in movieDataItems:
            #log_debug("Checking if exists: %s)", md["path"])
            try:
                mi = MovieItem(md["path"])
            except FileNotFoundError:
                library.deleteItemById(md["id"])
                log_debug("Removed entry for deleted movie: %s)", md["path"])
            
        
    def __run_update__(self):   
        movies = self.getAllMovieFiles()
        library = self.getLibrary()
        for movie in movies:
            if(len(library.findItemByPath(movie)) != 1 or self.__config["update_existing"] == True):
                try:
                    log_debug("Unregistered movie: %s", movie)
                    mi = MovieItem(movie)
                    md = mi.getMovieData()                    
                    library.registerMovieData(md)
                except Exception as e:
                    log_error("Movie data exception: %s - %s", e, movie)
        
        
    def getAllMovieFiles(self):
        movieList = []
        fileList = self.getAllLibraryFiles()

        for checkFile in fileList:
            se = os.path.splitext(checkFile)
            extension = se[1].lower()
            if(extension in self.__all_movie_extensions):
                movieList.append(checkFile)

        return movieList
    
    #===========================================================================
    # List all files present under the library folders
    #===========================================================================
    def getAllLibraryFiles(self):
        answer = []
        for folder in self.__library_folders:
            files = glob.glob(folder + "/**/*.*", recursive=True)
            answer.extend(files)
        
        return answer
