'''
Created on 24 Apr 2022

@author: jackisback
'''
from datetime import datetime
import hashlib
import json
import logging
import os.path
import re
import subprocess
import sys
import time
import string
import moviefixer.configuration as conf

from moviefixer.logger import log, log_debug, log_info, log_warn, log_error
import shutil

class MovieItem(object):
    __ffmpeg_bin:string = conf.getValue("ffmpeg_bin", "/usr/bin/ffmpeg")
    __ffprobe_bin = conf.getValue("ffprobe_bin", "/usr/bin/ffprobe")
    __tmp_folder = conf.getValue("tmp_folder", "/tmp")
    __original_file_path = None


    def __init__(self, file_path: string):
        self.__original_file_path = file_path
        
        if(os.path.isfile(self.__original_file_path) is False):
            raise FileNotFoundError("File not found", self.__original_file_path)
        
        #log_debug("Initialized(%s).", self.__original_file_path)
    
    
    def changeMovieContainer(self, container_extension):
        file_name_noext = os.path.splitext(os.path.basename(self.__original_file_path))[0]
        tmp_location = "{}/{}.{}".format(self.__tmp_folder, file_name_noext, container_extension)
        #output_path = os.path.dirname(self.__original_file_path) + '/' + '___' + file_name + '.' + container_extension
        
        ffmpeg_args = [
            '-hide_banner', 
            '-loglevel', 'fatal',
            '-fflags', '+genpts+igndts', 
            '-y', 
            '-i', self.__original_file_path,
            '-c', 'copy', 
            tmp_location
        ]
        
        try:
            self.__run_ffmpeg(ffmpeg_args)
        except RuntimeError as err:
            if(os.path.isfile(tmp_location) is True):
                os.remove(tmp_location)
        
        if(os.path.isfile(tmp_location) is True):
            # Substitute original movie with the new one
            os.remove(self.__original_file_path)
            final_location = "{}/{}.{}".format(os.path.dirname(self.__original_file_path), file_name_noext, container_extension)
            shutil.move(tmp_location, final_location)
            self.__original_file_path = final_location
    
    def transcodeAudioStreamsByIndex(self, indices:list):
        file_name = os.path.basename(self.__original_file_path)
        tmp_location = "{}/{}".format(self.__tmp_folder, file_name)
        
        ffmpeg_args = [
            '-hide_banner', 
            '-loglevel', 'fatal',
            '-fflags', '+genpts+igndts',
            '-y', 
            '-i', self.__original_file_path,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-map', '0',
        ]
        # "-c:0 aac -metadata:s:0 title=Italiano (AAC)
        for item in indices:
            stream_index, codec, title = item
            ffmpeg_args.append('-c:{}'.format(stream_index))
            ffmpeg_args.append('{}'.format(codec))
            ffmpeg_args.append('-metadata:s:{}'.format(stream_index))
            ffmpeg_args.append('title={}'.format(title))
        
        ffmpeg_args.append(tmp_location)
        log_debug("Audio transcode - Args: %s", ffmpeg_args)
        
        try:
            #pass
            self.__run_ffmpeg(ffmpeg_args)
        except RuntimeError as err:
            if(os.path.isfile(tmp_location) is True):
                os.remove(tmp_location)
                
        if(os.path.isfile(tmp_location) is True):
            # Substitute original movie with the new one
            os.remove(self.__original_file_path)
            final_location = "{}/{}".format(os.path.dirname(self.__original_file_path), file_name)
            shutil.move(tmp_location, final_location)
        
    
    def removeStreamsByIndex(self, indices:list):
        file_name = os.path.basename(self.__original_file_path)
        tmp_location = "{}/{}".format(self.__tmp_folder, file_name)
        #output_path = os.path.dirname(self.__original_file_path) + '/' + '___' + os.path.basename(self.__original_file_path)
        
        ffmpeg_args = [
            '-hide_banner', 
            '-loglevel', 'fatal',
            '-fflags', '+genpts+igndts', 
            '-y', 
            '-i', self.__original_file_path,
            '-c', 'copy', 
            '-map', '0',
        ]
        
        # Add '-map', '-0:3' for each stream to be removed
        for i in indices:
            ffmpeg_args.append('-map')
            ffmpeg_args.append('-0:{}'.format(i))
            
        ffmpeg_args.append(tmp_location)
        #log_debug("Args: %s", process_args)
        
        try:
            self.__run_ffmpeg(ffmpeg_args)
        except RuntimeError as err:
            if(os.path.isfile(tmp_location) is True):
                os.remove(tmp_location)

        if(os.path.isfile(tmp_location) is True):
            # Substitute original movie with the new one
            os.remove(self.__original_file_path)
            final_location = "{}/{}".format(os.path.dirname(self.__original_file_path), file_name)
            shutil.move(tmp_location, final_location)
            self.__original_file_path = final_location
        
    
    def getMovieData(self, moviePath = None):
        if(moviePath == None):
            moviePath = self.__original_file_path

        md = self.getMovieFormatData(moviePath)
        # log_debug("Movie Format Data: %s", json.dumps(md, indent=2, sort_keys=True))

        answer = {
            'id': self.getIdTag(), 
            'path': self.__original_file_path, 
            'title': self.__getSpecificKeyFromMovieData(md, "format.tags.title"),
            'bit_rate': int(self.__getSpecificKeyFromMovieData(md, "format.bit_rate")),
            'duration': int(float(self.__getSpecificKeyFromMovieData(md, "format.duration"))),
            'format_name': self.__getSpecificKeyFromMovieData(md, "format.format_name"),
            'size': int(self.__getSpecificKeyFromMovieData(md, "format.size")),
            'codec_name': self.__getSpecificKeyFromMovieData(md, "streams.0.codec_name"),
            'width': self.__getSpecificKeyFromMovieData(md, "streams.0.width"),
            'height': self.__getSpecificKeyFromMovieData(md, "streams.0.height"),
            'coded_width': self.__getSpecificKeyFromMovieData(md, "streams.0.coded_width"),
            'coded_height': self.__getSpecificKeyFromMovieData(md, "streams.0.coded_height"),
            'display_aspect_ratio': self.__getSpecificKeyFromMovieData(md, "streams.0.display_aspect_ratio"),
            'streams': []
        }
        
        
        streams:list = self.__getSpecificKeyFromMovieData(md, "streams")
        for stream in streams:
            md_stream = {
                'index': self.__getSpecificKeyFromMovieData(stream, "index"),
                'codec_type': self.__getSpecificKeyFromMovieData(stream, "codec_type"),
                'codec_name': self.__getSpecificKeyFromMovieData(stream, "codec_name"),
                'codec_long_name': self.__getSpecificKeyFromMovieData(stream, "codec_long_name"),
                'language': self.__getSpecificKeyFromMovieData(stream, "tags.language"),
                'title': self.__getSpecificKeyFromMovieData(stream, "tags.title")
            }
            answer['streams'].append(md_stream)
        
        #log_debug("Movie Data: %s", json.dumps(answer, indent=2, sort_keys=False))

        return answer
    
    #===========================================================================
    # Get information from the movie file using ffprobe
    #===========================================================================
    def getMovieFormatData(self, moviePath):
            ffprobe_args = [
                '-hide_banner', 
                '-v', 'quiet',
                '-loglevel', 'fatal', 
                '-print_format', 'json', 
                '-show_format', 
                '-show_streams',
                moviePath
            ]
            return self.__run_ffprobe(ffprobe_args)
    
    
    def __run_ffmpeg(self, app_args):
        process_args = [self.__ffmpeg_bin] + app_args
        process_out = subprocess.run(process_args, encoding='utf-8', stdout=subprocess.PIPE)
        
        if(process_out.returncode != 0):
            log_warn("Failed to run ffmpeg process!")
            log_debug("ffmpeg args: %s", process_args)
            raise RuntimeError("ffmpeg exec failed!")
    
        
    def __run_ffprobe(self, app_args):
        answer = None
        process_args = [self.__ffprobe_bin] + app_args
        process_out = subprocess.run(process_args, encoding='utf-8', stdout=subprocess.PIPE)
        if(process_out.returncode == 0):
            #log_debug("%s", process_out.stdout)
            answer = json.loads(process_out.stdout)

        return answer
        
        
    def __getSpecificKeyFromMovieData(self, movieData, dotted_key_path, default = ""):
        keys = dotted_key_path.split(".")
        dataBlock = movieData
        for key in keys:
            if(key.isdigit()):
                key = int(key)

            if(key in dataBlock or (isinstance(dataBlock, list) and key < len(dataBlock))):
                dataBlock = dataBlock.__getitem__(key)
                #log_debug("dataBlock(key=%s): %s", key, dataBlock)
            else:
                log_warn("No key in dataBlock(key=%s) when finding: %s", key, dotted_key_path)
                dataBlock = default
                break
        
        answer = dataBlock
        return answer
        
    
    def getIdTag(self):
        return hashlib.md5(self.__original_file_path.encode('utf-8')).hexdigest()

