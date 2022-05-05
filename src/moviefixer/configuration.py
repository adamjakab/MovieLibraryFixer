'''
Created on 27 Apr 2022

@author: jackisback
'''
import json

__configuration:object = {}


def getValue(dotted_key_path, default=""):
    keys = dotted_key_path.split(".")
    dataBlock = __configuration
    for key in keys:
        if(key.isdigit()):
            key = int(key)
        if(key in dataBlock or (isinstance(dataBlock, list) and key < len(dataBlock))):
            dataBlock = dataBlock.__getitem__(key)
        else:
            dataBlock = default
            break
    
    return dataBlock

def getConfig():
    return __configuration

def load_configuration(config_file, mode):
    print(">>>LOADING CONF")
    global __configuration
    f = open(config_file)
    data = json.load(f)
    f.close()
    __configuration = data[mode]
