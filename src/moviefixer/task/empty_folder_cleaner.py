'''
Copyright: Copyright (c) 2022., Adam Jakab

@author: Adam Jakab <adam at jakab dot pro>
@created: 23/4/2022, 10:19 AM
@license: See LICENSE.txt

@summary: Deletes empty folders
'''

import glob
import json
import os
from moviefixer.task import Task
from moviefixer.logger import log, log_debug, log_info, log_warn, log_error


class EmptyFolderCleanerTask(Task):
    __library_folders = []

    def __init__(self, library, stop_event):
        super(EmptyFolderCleanerTask, self).__init__(library, stop_event)
        
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
        
        if "expected_extensions" not in self.__config:
            raise Exception("Configuration parameter 'expected_extensions' is not defined.")
        
        self.__library_folders = self.__config["folders"]
        log_debug("Configured: %s", json.dumps(self.__config))
        
    
    def run(self):
        log("Running...")
        folders = self.__getLibraryFoldersWithoutMovies()
        log(folders)
        
        
        log("Done.")
    
    def __do_iteration(self, index):
        log("Doing iteration %s...", index)
        
    
    def __getLibraryFoldersWithoutMovies(self):
        answer = []
        folders = self.__getLibraryFoldersWithoutSubfolders()
        expected_extensions = self.__config["expected_extensions"]
        for folder in folders:
            files = glob.glob(folder + "*.*", recursive=True)
            extensions = [os.path.splitext(os.path.basename(f))[1].replace(".", "") for f in files]
            #log_debug("Ext(%s): %s", folder, extensions)
            if set(extensions).isdisjoint(expected_extensions):
                answer.append(folder)
                
        return answer
            

    def __getLibraryFoldersWithoutSubfolders(self):
        answer = []
        folders = self.__getLibraryFolders()
        for folder in folders:
            subfolders = glob.glob(folder + "*/", recursive=True)
            if len(subfolders) == 0:
                answer.append(folder)
        
        return answer
    
    
    def __getLibraryFolders(self):
        answer = []
        for folder in self.__library_folders:
            files = glob.glob(folder + "/**/", recursive=True)
            answer.extend(files)
        
        return answer
    