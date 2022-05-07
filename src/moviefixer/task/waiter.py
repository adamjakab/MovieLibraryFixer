'''
Copyright: Copyright (c) 2022., Adam Jakab

@author: Adam Jakab <adam at jakab dot pro>
@created: 23/4/2022
@license: See LICENSE.txt

@summary: Wait Module (for testing process timeout).
'''

import json
from iso639 import languages
from moviefixer.task import Task
from moviefixer.movieitem import MovieItem
from moviefixer.logger import log, log_debug, log_info, log_warn, log_error
import time


class WaiterTask(Task):

    def __init__(self, library, stop_event):
        super(WaiterTask, self).__init__(library, stop_event)
        
    def configure(self, params):
        self.__config = params
        if "iterations" not in self.__config:
            raise Exception("Configuration parameter 'iterations' is not defined.")
        if "wait_time" not in self.__config:
            raise Exception("Configuration parameter 'wait_time' is not defined.")
        
        log_debug("Configured: %s", json.dumps(self.__config)) 
        

    def run(self):
        log("Running...")
        i = 0
        while i < self.__config["iterations"]:
            if self.isStopRequested():
                log_info("Task stopped.")
                break;
            i = i + 1
            self.__do_iteration(i)
                
        log("Done.")
    
    def __do_iteration(self, index):
        log("Doing iteration %s...", index)
        time.sleep(self.__config["wait_time"])
        