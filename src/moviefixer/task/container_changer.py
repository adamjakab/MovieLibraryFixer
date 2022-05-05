'''
Copyright: Copyright (c) 2022., Adam Jakab

@author: Adam Jakab <adam at jakab dot pro>
@created: 23/4/2022, 10:19 AM
@license: See LICENSE.txt
'''

import json
import os
from moviefixer.task import Task
from moviefixer.movieitem import MovieItem
from moviefixer.logger import log, log_debug, log_info, log_warn, log_error

class ContainerChangerTask(Task):

    def __init__(self, library):
        super(ContainerChangerTask, self).__init__(library)
        
        
    def configure(self, params):
        self.__config = params
        if "container" not in self.__config:
            raise Exception("Configuration parameter 'container' is not defined.")
        
        log_debug("Configured: %s", json.dumps(self.__config)) 


    def run(self):
        log("Running...")
        library = self.getLibrary()
        movieDataItems = library.getAllItems()
        for md in movieDataItems:
            self.__verify_item(md)
                
        log("Done.")
        
        
    def __verify_item(self, md):
        file_extension = os.path.splitext(os.path.basename(md["path"]))[1].strip('.')
        if (file_extension == self.__config["container"]):
            return
            
        mi = MovieItem(md["path"])
        try:
            mi.changeMovieContainer(self.__config["container"])
        except Exception as err:
                log_debug("Error changing container! %s Skipping.", err)
        
        
        # re-register updated movie data in library
        # @todo: should remove old movie (.avi) from library which was converted
        md = mi.getMovieData()
        library = self.getLibrary()                 
        library.registerMovieData(md)
