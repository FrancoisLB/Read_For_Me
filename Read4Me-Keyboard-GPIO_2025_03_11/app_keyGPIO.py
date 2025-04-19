#!/usr/bin/python
#
# PiTextReader - Raspberry Pi Printed Text-to-Speech Reader
#
# Allows sight impaired person to have printed text read using
# OCR and text-to-speech.
#
# Normally run by pi crontab at bootup
# Turn off by commenting out @reboot... using $ crontab -e; sudo reboot
# Manually run using $ python pitextreader.py
#
# This is a simplistic (i.e. not pretty) python program
# Just runs cmd-line pgms raspistill, tesseract-ocr, flite to do all the work
#
# Version 1.0 2018.02.10 - initial release - rgrokett
# v1.1 - added some text cleanup to improve reading
# v1.2 - removed tabs
#
# http://kd.grokett.com/
#
# License: GPLv3, see: www.gnu.org/licenses/gpl-3.0.html
#

import sys
import os
import time
from logger import logger
from app import App
from constantes import SOUNDS
from constantes import CB
from player import Player
from keypad_GPIO import Key_GPIO

# key map with callback functions
tab_keyboard= {
    CB.CAPTURE:'1',
    CB.PLAY_START_STOP:'4',
    CB.VOLUME_INC:'3',
    CB.VOLUME_DEC:'2',
    CB.SPEED_INC:'6',
    CB.SPEED_DEC:'5',       
    CB.FORWARD:'9',
    CB.BACKWARD:'8',
    CB.ON_OFF:'0',
    CB.CANCEL:'7'
}

# Vérifie si la caméra est détectée par le système
try:
    result = os.popen("libcamera-hello --list-cameras").read()
    result.index("Available cameras")  # Lève une exception si la chaîne n'est pas trouvée
    print("Caméra détectée !")
    erreur_camera = False
except ValueError:
    print("Erreur lors de la vérification de la caméra : Aucune caméra détectée")
    erreur_camera = True
except Exception as e:
    erreur_camera = True
    print(f"Erreur lors de la vérification de la caméra : {e}")

# Vérifie si l'enceinte est détectée par le système
try:
    result = os.popen("aplay -l").read()
    result.index("USB")  # Lève une exception si "USB" n'est pas trouvé
    print("Enceinte détectée !")
except ValueError:
    print("Erreur lors de la vérification de l'enceinte : Aucune enceinte USB détectée")
    sys.exit()
except Exception as e:
    print(f"Erreur lors de la vérification de l'enceinte : {e}")
    sys.exit()

######
# MAIN
######

try:
    app = App(keyGPIO = Key_GPIO(tab_keyboard))
    
    if erreur_camera == True:
        app.player.play(SOUNDS + 'erreur-camera')
        time.sleep(2)
        sys.exit()

    app.settings.set_volume_play()
    app.start()
    print("start")
    app.player.play(SOUNDS + 'ready')
    while True:
        time.sleep(1)
        app.wait()
    # end while

except (KeyboardInterrupt, SystemExit):
    logger.info("exiting")
    app.close()

    sys.exit(0)
