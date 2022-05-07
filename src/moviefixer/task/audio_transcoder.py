'''
Copyright: Copyright (c) 2022., Adam Jakab

@author: Adam Jakab <adam at jakab dot pro>
@created: 23/4/2022
@license: See LICENSE.txt

@summary: Converts all audio streams to the required format and sets the stream title accordingly.
'''

import json
from iso639 import languages
from moviefixer.task import Task
from moviefixer.movieitem import MovieItem
from moviefixer.logger import log, log_debug, log_info, log_warn, log_error
import string


class AudioTranscoderTask(Task):

    def __init__(self, library, stop_event):
        super(AudioTranscoderTask, self).__init__(library, stop_event)
        
    def configure(self, params):
        self.__config = params
        if "codec" not in self.__config:
            raise Exception("Configuration parameter 'codec' is not defined.")
        
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
        transcode_streams = []
        
        for stream in md["streams"]:
            if stream["codec_type"] == "audio":
                stream_index = stream["index"]
                stream_lang = stream["language"]
                stream_title = self.__getStreamTitle(stream_lang, self.__config["codec"])
                if stream["codec_name"] != self.__config["codec"] or stream["title"] != stream_title:
                    stream_codec = stream["codec_name"]
                    if stream_codec != self.__config["codec"]:
                        stream_codec = self.__config["codec"]
                    else:
                        stream_codec = "copy"
                        
                    transcode_streams.append([stream_index, stream_codec, stream_title])
                
        if (len(transcode_streams) == 0):
            return 
        
        mi = MovieItem(md["path"])
        log("Movie '%s' need audio transcoding for streams: %s", md["title"], transcode_streams)
        try:
            mi.transcodeAudioStreamsByIndex(transcode_streams)
        except RuntimeError as err:
                log_debug("Error removing streams! %s Skipping.", err)
                
        # re-register updated movie data in library
        mi = MovieItem(md["path"])
        md = mi.getMovieData()
        library = self.getLibrary()                 
        library.registerMovieData(md)
    
    def __getStreamTitle(self, lang_code:string, codec):
        language = "Unknown"
        if lang_code and lang_code.strip():
            try:
                iso639Lang = languages.get(part3=lang_code)
                language = iso639Lang.name
            except KeyError:
                try:
                    iso639Lang = languages.get(part2b=lang_code)
                    language = iso639Lang.name
                except KeyError:
                    try:
                        iso639Lang = languages.get(part1=lang_code)
                        language = iso639Lang.name
                    except KeyError:
                        log_debug("No match found for ISO-639 language with code: '%s'", lang_code)
        
        answer = "{} ({})".format(language, codec.upper())
        return answer
        
