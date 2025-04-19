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
        try:
            f = open(CONFIG_FILE,"r")
            self.data = json.loads(f.read())
            f.close()
        except Exception as e:
            self.data = DEFAULT_SETTINGS
            self.timer = 1
        # end try

        # set default value if value is not set in current file
        for key, value in DEFAULT_SETTINGS.items():
            if key not in self.data:
                self.data[key] = value

    # VOLUME ####################################################
    def set_volume(self, val):
        """
        Set volume between 0 and 100%
        """
        vol = int(val)
        if vol < 0:
            vol = 0
        elif vol > 100:
            vol = 100
        logger.info('VOL ' + str(vol))
        self.player.volume_set(vol)

    def volume_inc(self):
        """
        Raise reading volume
        """
        self.data['volume'] += 4
        self.set_volume_play()
        self.save()

    def volume_dec(self):
        """
        Lower reading volume
        """
        self.data['volume'] -= 4
        self.set_volume_play()
        self.save()

    def set_volume_play(self):
        """
        Set current volume to reading volume
        """
        self.set_volume(self.data['volume'])

    def set_volume_help(self):
        """
        Set current volume to help volume
        """
        self.set_volume(self.data['volume_help'])

    # speed ####################################################
    def speed_inc(self):
        """
        Raise reading speed, and save
        """
        self.data['speed'] *= 1.25
        self.player.speed_set(self.data['speed'])
        logger.info('speed: %s' % self.data['speed'])
        self.save()

    def speed_dec(self):
        """
        Raise reading speed, and save
        """
        self.data['speed'] *= 0.8
        self.player.speed_set(self.data['speed'])
        logger.info('speed: %s' % self.data['speed'])
        self.save()

    def save(self):
        """
        Save current settings in config file
        """
        try:
            f = open(CONFIG_FILE, "w")
            f.write(json.dumps(self.data))
            f.close()
        except Exception as e:
            pass


class App():
    """
    Main app for PiTextReader

    - initialize controlers objects: player, settings
    - define association between GPIO and callbacks
    - handle capture to speech process
    """
    def __init__(self, keyGPIO):
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

        self.keyGPIO = keyGPIO

        self.shutdown_click = False

        logger.info('app.init')

    def link_buttons(self):
        if self.buttons: 
            for key in self.buttons.dict_callback:
                callback=self.callbacks[key.value]
                self.buttons.link(self.buttons.dict_callback[key],callback)
    
    def start(self):
        self.keyGPIO.start()
        self.keyGPIO.links(self.callbacks)
        
    def wait(self):
        """Attend les entrées clavier sans bloquer"""
        print("En attente d'une touche... ")
        if self.keyGPIO is not None:
            print("Confilg_file : ",CONFIG_FILE)
            self.keyGPIO.listen()

    def play_start_stop_cb(self):
        """
        Start and pause audio player
        TODO restart if paused, start over if ended
        """
        logger.info('Play start stop')
        # Start reading text
        #self.settings.set_volume_play()
        #self.player.play(self.basename)
        self.player.pause()

    def capture(self):
        """
        Main process from image capture to speech:
        1. Capture an image
        2. OCR to text
        3. Text to speech
        4. Start audio player
        """
        logger.info('app.capture')

        # 1. Capture an image

        # Take photo
        self.settings.set_volume_play()
        self.player.play(SOUNDS + "camera-shutter")
        reader.snapshot(self.basename)
        logger.info('app.capture.snapshot')

        # OCR to text
        # play message to say the process started
        self.player.play(SOUNDS + "ocr")
        time.sleep(1)

        # play waiting song
        self.player.play(SOUNDS + "orange", extension="mp3")

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
                self.player.play(self.basename)
            else:
                raise Exception('audio file empty')
        except:
            logger.error("Cannot read")
            self.player.play(SOUNDS + "erreur")

        return

    def cancel_cb(self):
        """
        Stop the capture process
        """
        logger.info('app.Cancel')
        self.player.play(SOUNDS + 'cancel')
        return

    def shutdown(self):
        """
        Ask for confirmation, then shutdown the system
        TODO set a timer to cancel if shutdown is not confirmed
        """
        if not self.shutdown_click:
            self.player.play(SOUNDS + 'shutdown')
            self.shutdown_click = True
        else:
            os.system('sudo shutdown now')

    def close(self):
        logger.info('app.Close')
        self.player.stop()
        self.player.close()
