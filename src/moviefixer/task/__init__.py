#  Copyright: Copyright (c) 2022., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 23/4/2022, 10:19 AM
#  License: See LICENSE.txt
#
from abc import ABC
from abc import abstractmethod
from moviefixer.logger import log_debug

class Task(ABC):
    __movie_library = None
    __stop_event = None
    __config = {}
    
    def __init__(self, library, stop_event):
        self.__movie_library = library
        self.__stop_event = stop_event
        
    def getLibrary(self):
        return self.__movie_library
    
    def getStopEvent(self):
        return self.__stop_event
    
    def isStopRequested(self):
        return self.__stop_event.is_set()
        
    @abstractmethod
    def configure(self, params):
        raise NotImplementedError("You must implement this method.")

    @abstractmethod
    def run(self):
        raise NotImplementedError("You must implement this method.")
    
    