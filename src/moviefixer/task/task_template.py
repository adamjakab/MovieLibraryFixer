'''
Copyright: Copyright (c) 2022., Adam Jakab

@author: Adam Jakab <adam at jakab dot pro>
@created: xx/xx/2022
@license: See LICENSE.txt

@summary: Task Template
'''

import json
import time
from moviefixer.task import Task
from moviefixer.logger import log, log_debug, log_info, log_warn, log_error


class TaskTemplateTask(Task):

    def __init__(self, library, stop_event):
        super(TaskTemplateTask, self).__init__(library, stop_event)
        
    def configure(self, params):
        self.__config = params
        # if "myparam" not in self.__config:
            # raise Exception("Configuration parameter 'myparam' is not defined.")
        
        log_debug("Configured: %s", json.dumps(self.__config))
        
    
    def run(self):
        log("Running...")
        i = 0
        while i < 5:
            if self.isStopRequested():
                log_info("Task stopped.")
                break;
            i = i + 1
            self.__do_iteration(i)
                
        log("Done.")
    
    def __do_iteration(self, index):
        log("Doing iteration %s...", index)
        time.sleep(1)