#  Copyright: Copyright (c) 2022., Adam Jakab
#
#  Author: Adam Jakab <adam at jakab dot pro>
#  Created: 23/4/2022, 10:19 AM
#  License: See LICENSE.txt
#
from abc import ABC
from abc import abstractmethod

class Task(ABC):
    __movie_library = None
    __config = {}
    
    def __init__(self, library):
        self.__movie_library = library
        
    def getLibrary(self):
        return self.__movie_library
        
    @abstractmethod
    def configure(self, params):
        raise NotImplementedError("You must implement this method.")

    @abstractmethod
    def run(self):
        raise NotImplementedError("You must implement this method.")
    
    