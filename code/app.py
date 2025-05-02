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
 It provides methods for capturing images, performing OCR,
 and converting text to speech.
 It also handles volume and speed adjustments for the audio playback.
"""
import os
import time
import json
from logger import logger
from constantes import CONFIG_FILE, DEFAULT_SETTINGS, SOUNDS, FILTER_SETTINGS
from player import Player
import reader

class Settings:
    """
    Handle volume and speed settings
    use default settings if they are not saved in config file
    save settings in config files

    3 default volumes are defined:
    - play volume: volume for reading the text (the volume that can be
    set by user)
    - help volume: volume for help message
    - song volume: volume for the waiting song
    """
    def __init__(self, player):
        """
        Init, set mplayer instance and read saved or recorded settings
        """
        self.player = player
        # read config file, fallback to default settings

        with open(CONFIG_FILE, "r", encoding='utf-8') as f:
            try:
                self.data = json.loads(f.read())
            except (FileNotFoundError, json.JSONDecodeError):
                self.data = DEFAULT_SETTINGS
                self.timer = 1
        # set default value if value is not set in current file
        for key, value in DEFAULT_SETTINGS.items():
            if key not in self.data:
                self.data[key] = value

    def set_volume(self, val:int) -> None:
        """
        Set volume between 0 and 100%
        
        Parameters:
        -----------
        val: int
            The volume level to set (0-100) 
    
        Returns:
        --------
        None
        """
        self.player.set_volume(int(val))

    def volume_inc(self) -> None:
        """ 
        Raise reading volume
        """
        self.data['volume'] += 4
        self.set_volume_play()
        self.save()

    def volume_dec(self) -> None:
        """ 
        Lower reading volume
        """
        self.data['volume'] -= 4
        self.set_volume_play()
        self.save()

    def set_volume_play(self) -> None:
        """
        Set current volume to reading volume
        """
        self.set_volume(self.data['volume'])

    def set_volume_help(self) -> None:
        """
        Set current volume to help volume
        """
        self.set_volume(self.data['volume_help'])


    def speed_inc(self) -> None:
        """
        Raise reading speed, and save
        """
        self.data['speed'] *= 1.25
        self.player.set_speed(self.data['speed'])
        self.save()

    def speed_dec(self) -> None:
        """
        Raise reading speed, and save
        """
        self.data['speed'] *= 0.8
        self.player.set_speed(self.data['speed'])
        self.save()

    def save(self) -> None:
        """
        Save current settings in config file
        """
        with open(CONFIG_FILE, "w", encoding='utf-8') as f:
            try:
                f.write(json.dumps(self.data))
            except (OSError, IOError, json.JSONDecodeError):
                logger.error("Failed to save settings to config file")

class App():
    """
    App class to handle the main application logic for the Read For Me project.
    This class manages the interaction between the user, the GPIO keypad,
    and the audio playback system.
    It provides methods for capturing images, performing OCR,
    and converting text to speech.
    It also handles volume and speed adjustments for the audio playback.
    """
    def __init__(self, keyboard) -> None:
        """
        Init, set mplayer instance and read saved or recorded settings
        """
        self.basename = '/tmp/scan'
        self.player = Player()
        self.settings = Settings(self.player)
        # Must be coherent with constantes.CB
        self.callbacks=[self.shutdown,
                        self.capture,
                        self.settings.volume_dec,
                        self.settings.volume_inc,
                        self.play_start_stop_cb,
                        self.settings.speed_dec,
                        self.settings.speed_inc,
                        self.cancel_cb,
                        self.player.backward,
                        self.player.forward
                        ]
        self.keyboard = keyboard
        self.shutdown_click = False
        logger.info('app.init')

    def start(self) -> None:
        """
        Start the application
        """
        self.keyboard.start()
        self.keyboard.links(self.callbacks)

    def wait(self) -> None:
        """ 
        Wait for keyboard input
        This function is non-blocking and allows the application to continue
        running while waiting for user input.
        It uses the keyboard instance to listen for key presses and trigger
        the corresponding callback functions.
        """
        print("Waiting a key ...")
        if self.keyboard is not None:
            print("Config_file : ",CONFIG_FILE)
            self.keyboard.listen()

    def play_start_stop_cb(self) -> None:
        """
        Start and pause audio player
        TODO restart if paused, start over if ended
        """
        logger.info('Play start stop')
        # Start reading text
        #self.settings.set_volume_play()
        #self.player.play(self.basename)
        self.player.pause()

    def capture(self) -> None:
        """
        Main process from image capture to speech:
        1. Capture an image
        2. OCR to text
        3. Text to speech
        4. Start audio player
        """
        logger.info('app.capture')

        # 1. Capture an image
        # Take a picture
        self.settings.set_volume_play()
        self.player.play(SOUNDS + "camera-shutter.wav")
        reader.snapshot(self.basename)
        logger.info('app.capture.snapshot')
        # OCR to text
        # play message to say the process started
        self.player.play(SOUNDS + "ocr.wav")
        time.sleep(1)
        # play waiting song
        self.player.play(SOUNDS + "orange.mp3")

        # 2. OCR to text
        reader.ocr_to_text(self.basename, FILTER_SETTINGS['rotation'], FILTER_SETTINGS['filter'])
        # stop song
        self.player.stop()
        time.sleep(0.5)

        try:
            # Cleanup text
            reader.clean_text(self.basename)
            # 3. Text to speech
            reader.text_to_sound(self.basename)
            # 4. Start audio player
            if os.stat("/tmp/scan.txt").st_size != 0:
                self.player.play(self.basename+'.wav')
            else:
                raise ValueError('audio file is empty')
        except (FileNotFoundError, ValueError, OSError) as e:
            logger.error("Cannot read: %s", e)
            self.player.play(SOUNDS + "erreur.wav")


    def cancel_cb(self) -> None:
        """
        Stop the capture process
        """
        logger.info('app.Cancel')
        self.player.play(SOUNDS + 'cancel')


    def shutdown(self) -> None:
        """
        Ask for confirmation, then shutdown the system
        TODO set a timer to cancel if shutdown is not confirmed
        """
        if not self.shutdown_click:
            self.player.play(SOUNDS + 'shutdown.wav')
            self.shutdown_click = True
        else:
            os.system('sudo shutdown now')

    def close(self) -> None:
        """
        Close the application and clean up resources
        """
        logger.info('app.Close')
        self.player.stop()
        self.player.close()
