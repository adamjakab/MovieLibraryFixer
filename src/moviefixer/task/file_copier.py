'''
Copyright: Copyright (c) 2022., Adam Jakab

@author: Adam Jakab <adam at jakab dot pro>
@created: 23/4/2022, 10:19 AM
@license: See LICENSE.txt
'''

import json
import os
import glob
from moviefixer.task import Task
from moviefixer.movieitem import MovieItem
from moviefixer.logger import log, log_debug, log_info, log_warn, log_error
from posix import mkdir
import shutil

class FileCopierTask(Task):

    def __init__(self, library, stop_event):
        super(FileCopierTask, self).__init__(library, stop_event)
        
        
    def configure(self, params):
        self.__config = params
        if "source_folders" not in self.__config:
            raise Exception("Configuration parameter 'source_folders' is not defined.")
        if "destinaion_folder" not in self.__config:
            raise Exception("Configuration parameter 'destinaion_folder' is not defined.")
        if "extensions" not in self.__config:
            raise Exception("Configuration parameter 'extensions' is not defined.")
        
        log_debug("Configured: %s", json.dumps(self.__config)) 


    def run(self):
        log("Running...")
        
        # Ensure destination folder exists
        if(os.path.isdir(self.__config["destinaion_folder"]) is False):
            log_debug("Creating destination folder: %s", self.__config["destinaion_folder"])
            os.makedirs(self.__config["destinaion_folder"])
        
        files_to_move = self.getAllSourceFiles()
        for file_path in files_to_move:
            self.__move_file(file_path)
            
        # @todo: clean up source folders?
        
        log("Done.")
        
        
    def __move_file(self, file_path):
        new_file_path = os.path.realpath(self.__config["destinaion_folder"]) + '/' + os.path.basename(file_path)
        log_debug("Moving file %s to: %s", file_path, new_file_path)
        shutil.move(file_path, new_file_path)
        
        # Register movie data in library
        mi = MovieItem(new_file_path)
        md = mi.getMovieData()
        library = self.getLibrary()                 
        library.registerMovieData(md)
            
    #===========================================================================
    # List all files present under the library folders
    #===========================================================================
    def getAllSourceFiles(self):
        answer = []
        for folder in self.__config["source_folders"]:
            for extension in self.__config["extensions"]:
                pattern = "{f}/**/*.{e}".format(f=folder, e=extension)
                files = glob.glob(pattern, recursive=True)
                answer.extend(files)
        
        return answer
