'''
Copyright: Copyright (c) 2022., Adam Jakab

@author: Adam Jakab <adam at jakab dot pro>
@created: 23/4/2022, 10:19 AM
@license: See LICENSE.txt
'''

import json
from moviefixer.task import Task
from moviefixer.logger import log, log_debug, log_info, log_warn, log_error

class TaskTemplateTask(Task):

    def __init__(self, library):
        super(TaskTemplateTask, self).__init__(library)
        
        
    def configure(self, params):
        self.__config = params       
        log_debug("Configured: %s", json.dumps(self.__config)) 


    def run(self):
        log("Running...")
        log("Done.")
