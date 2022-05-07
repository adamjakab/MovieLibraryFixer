'''
Copyright: Copyright (c) 2022., Adam Jakab

@author: Adam Jakab <adam at jakab dot pro>
@created: 23/4/2022, 10:19 AM
@license: See LICENSE.txt
'''

import json
from moviefixer.task import Task
from moviefixer.movieitem import MovieItem
from moviefixer.logger import log, log_debug, log_info, log_warn, log_error

class StreamCleanerTask(Task):

    def __init__(self, library, stop_event):
        super(StreamCleanerTask, self).__init__(library, stop_event)
        
        
    def configure(self, params):
        self.__config = params
        if "allowed_codec_types" not in self.__config:
            raise Exception("Configuration parameter 'allowed_codec_types' is not defined.")
        
        log_debug("Configured: %s", json.dumps(self.__config)) 


    def run(self):
        log("Running...")
        
        library = self.getLibrary()
        movieDataItems = library.getAllItems()
        for md in movieDataItems:
            if self.isStopRequested():
                log_info("Task stopped.")
                break;
            self.__verify_item(md)
                
        log("Done.")
        
        
    def __verify_item(self, md):
        unallowed_stream_indices = []
        
        for stream in md["streams"]:
            if stream["codec_type"] not in self.__config["allowed_codec_types"]:
                unallowed_stream_indices.append(stream["index"])
                
        if (len(unallowed_stream_indices) == 0):
            return 
        
        log_debug("Item(%s) has unallowed streams: %s", md["path"], unallowed_stream_indices)
        mi = MovieItem(md["path"])
        try:
            mi.removeStreamsByIndex(unallowed_stream_indices)
        except RuntimeError as err:
                log_debug("Error removing streams! %s Skipping.", err)
        
        # re-register updated movie data in library
        md = mi.getMovieData()
        library = self.getLibrary()                 
        library.registerMovieData(md)
            
        
