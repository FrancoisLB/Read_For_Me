# Python code Read For Me which is dedicated to visualy impaired people
# to read A4 document, based on Raspberry PI.
# Copyright 2025 Read For Me
# Contributors: see AUTHORS file
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>
"""
Constants for the Read For Me project
This module contains constants and settings used throughout the project.
It includes command-line arguments, GPIO pin numbers, and other 
configuration settings.
"""

from enum import Enum
import os

DEBUG   = 1 # Debug 0/1 off/on (writes to debug.log)
class CB(Enum):
    """
    Enum for callback functions
    """
    CAPTURE=1
    PLAY_START_STOP=4
    VOLUME_INC=3
    VOLUME_DEC=2
    SPEED_INC=6
    SPEED_DEC=5
    FORWARD=9
    BACKWARD=8
    ON_OFF=0
    CANCEL=7

FILTER_SETTINGS={'rotation':True, 'filter':False}

DEFAULT_SETTINGS = {'volume': 96,
                   'volume_help' : 95,
                   'speed' : 1.0}

try:
    READFORME_PATH=os.environ['READFORME_PATH']
except KeyError:
    READFORME_PATH='.'

SOUNDS  = READFORME_PATH+'/sounds/'
CONFIG_FILE= READFORME_PATH+'/config.json'

CMD_MIXER = "amixer -q sset Headphone,0 "
CMD_CAMERA  = 'libcamera-still --rotation 180 -t 500 -o '
CMD_OCR = 'tesseract -l fra --psm 3'
CMD_SOUND = "/usr/bin/pico2wave -l fr-FR -w"
