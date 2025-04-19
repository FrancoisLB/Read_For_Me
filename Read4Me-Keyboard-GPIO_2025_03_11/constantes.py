from enum import Enum
import os

DEBUG   = 1 # Debug 0/1 off/on (writes to debug.log)
class CB(Enum):
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
