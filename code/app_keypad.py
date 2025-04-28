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
App class to handle the main application logic for the Read For Me project.
This class manages the interaction between the user, the GPIO keypad,
and the audio playback system.
"""
import sys
import os
import time
from logger import logger
from app import App
from constantes import SOUNDS
from constantes import CB
from keypad_gpio import KeypadGPIO

def app_run():
    """
    Main function to run the application.
    """

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

    # Check if the camera is detected
    try:
        result = os.popen("libcamera-hello --list-cameras").read()
        result.index("Available cameras")
        print("Camera detected !")
        erreur_camera = False
    except (ValueError,  OSError, RuntimeError) as e:
        print(f"Speaker detection error : {e}")
        erreur_camera = True
        sys.exit()
    # Check if the speaker is detected
    try:
        result = os.popen("aplay -l").read()
        result.index("USB")
        print("Speacker detected !")
    except (ValueError, OSError, RuntimeError) as e:
        print(f"Speaker detection error : {e}")
        sys.exit()

    # Launch the loop application
    try:
        app = App(keyboard = KeypadGPIO(tab_keyboard))

        if erreur_camera is True:
            app.player.play(SOUNDS + 'erreur-camera')
            time.sleep(2)
            sys.exit()

        app.settings.set_volume_play()
        app.start()
        app.player.play(SOUNDS + 'ready')
        while True:
            time.sleep(1)
            app.wait()
        # end while
    except (KeyboardInterrupt, SystemExit):
        logger.info("exiting")
        app.close()

        sys.exit(0)

if __name__ == "_main_":
    # Main function to run the application.
    app_run()
