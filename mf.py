#!/usr/bin/env python3
'''
Copyright: Copyright (c) 2022., Adam Jakab

@author: Adam Jakab <adam at jakab dot pro>
@created: 23/4/2022
@license: See LICENSE.txt

@summary: Main entry point for MovieFixer
'''

import sys
from pathlib import Path
import os
import traceback
import argparse
import logging, logging.config

# Add "src" to Sys Path for local imports
__projectdir__ = os.path.dirname(os.path.realpath(__file__))
sys.path.append(str(__projectdir__+"/src"))

# Local imports from src
from moviefixer import Moviefixer

# Variables
config_file = __projectdir__ + '/config/config.json'
mode = None


def main(config_file, mode):
    try:
        mf = Moviefixer(config_file, mode)
    except Exception as e:
        print("Exception: ", traceback.format_exc())
        sys.exit(1)


# Add command line arguments and run 
parser = argparse.ArgumentParser(description='Movie Fixer')
parser.add_argument('--mode', required=True, default=False, help='Select one of the run modes defined in the configuration file.')
parser.add_argument('--config', default=config_file, help='Set which configuration file to use.')
args = parser.parse_args()
# Check Parsed arguments
mode = args.mode
config_file = args.config
# Run main
main(config_file, mode)
