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
TextReader class to handle the main application logic for the Read For Me project.
This class manages the interaction between the user, the GPIO keypad,
and the audio playback system.
"""
import argparse
import time
import os
import sys
import toml
from player import Player
from reader import Reader
from logger import logger

class TextReader:
    """
    Readforme with reader and player 
    """
    def __init__(self, basename:str, play:bool=True):
        """ Constructor

        Args:
            basename (str): file basename with path
        """
        logger.info('TextReader:init')
        self.reader=Reader(basename)
        if play:
            self.player=Player(basename)
        else:
            self.player=None
        self.read_config()

    def set_base(self, basename:str, extension_reader:str='.jpg') -> None:
        """
        Set basename and extension
        
        Parameters:
        -----------
        basename: str
            The base name for the image and text files
        extension_reader: str
            The file extension for the image files
        extension_player: str
            The file extension for the audio files  
            
        Returns:
        --------
        None
        """
        self.reader.set_base(basename, extension_reader)

    def read_config(self) -> None:
        """ Read the config file
        """
        logger.info('Textreader:read_config')
        # Search config file
        home_dir = os.path.expanduser("~")
        config_file = 'readforme.toml'
        config_paths = [config_file, os.path.join(home_dir, config_file)]
    
        config_found = False
        for config_path in config_paths:
            print('Config file:', config_path)
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = toml.load(f)
                    print('Config file:', config)
                try:
                    if self.player:
                        self.player.volume=config['player']['volume']
                        self.player.volume_help=config['player']['volume_help']
                        self.player.speed=config['player']['speed']
                    self.path_sounds=config['general']['path_sounds']
                except KeyError:
                    self.play_text("Erreur dans le fichier de configuration")
                    logger.error('Textreader:read_config failure in config file')
                    sys.exit(1)
                config_found = True
                break
            except FileNotFoundError:
                logger.warning("Config file not found at %s", config_path)

        if not config_found:
            self.play_text("Fichier de configuration introuvable")
            logger.error('Textreader:read_config file not found')
            sys.exit(1)

    def play_sound(self, audiofilename:str) -> None:
        """
        Play a sound file
        
        Parameters:
        -----------
        audiofilename: str
            The name of the audio file to play
            
        Returns:
        --------
        None    
        
        """
        if self.player:
            self.player.play(os.path.join(self.path_sounds,audiofilename))

    def play_text(self, sentences:str) -> None:
        """
        Play text
        """
        self.reader.text_to_sound(sentences)
        if self.player:
            print('play_text', self.reader.file_txt_to_sound, sentences)
            self.player.play(self.reader.file_txt_to_sound)

    def sequence(self):
        """
        Main sequencefrom image capture to speech:
        1. Capture an image
        2. OCR to text
        3. Text to speech
        4. Start audio player
        """
        logger.info('TextReader:sequence')

        # 1. Take photo
        self.play_sound('camera-shutter.wav')
        self.player.reset_volume(help_sound=True)
        #self.reader.snapshot()

        # 2. OCR to text
        # play message to say the process started

        if os.path.isfile(self.reader.basename+self.reader.extension):
            self.play_sound('ocr.wav')
        else:
            logger.error('TextReader:sequence snapshot failed')
            self.play_text("La photo n'a pas été prise correctement. Veuillez recommencer")
            return
        time.sleep(1)

        # play waiting song
        self.play_sound('orange.mp3')

        # OCR to text
        if os.path.isfile(self.reader.basename+'_raw.txt') is False:
            logger.error('TextReader:sequence ocr failed')
            self.play_text("La numérisation n'a pas fonctionné correctement. Veuillez recommencer")
            return

        self.reader.ocr_to_text()

        # stop waiting song
        self.player.stop()
        time.sleep(1)

        # Cleanup text
        self.reader.clean_text()

        # 3. Text to speech
        self.reader.text_to_sound()

        # 4. Start audio player
        reader_audio_filename = self.reader.basename + '.wav'
        if os.path.isfile(reader_audio_filename) is False:
            logger.error('TextReader:sequence text to speech failed')
            self.play_text("La synthèse vocale n'a pas fonctionné correctement."\
                            "Veuillez recommencer")
        else:
            self.player.play(reader_audio_filename, blocking=True)
            self.player.reset_volume()
            self.player.reset_speed()


    def close(self) -> None:
        """
        Close the player
        """
        logger.info('TextReader:close')
        if self.player:
            self.player.close()

def test_sequence(rfm:TextReader):
    """ Test the sequence method of the TextReader class
    """
    try:
        # Démarrage
        rfm.play_text("OK, on est pret")
        rfm.player.reset_volume(help_sound=True)
        time.sleep(2)

        rfm.sequence()

        print("CTRL+C to exit")
        while True:
            time.sleep(2)
            if not rfm.player.is_playing():
                break
        rfm.play_text("OK, c'est fini")
        time.sleep(2)

    except KeyboardInterrupt:
        logger.info("exiting")
        rfm.close()
        sys.exit(0)

def main():
    """ Main function to run the TextReader application
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Scan printed text and converts to text speech')
    parser.add_argument('-b', '--basename', required=True,
                        help='file basename')
    parser.add_argument('-p', '--play', action='store_true',
                        help='play speech')
    parser.add_argument('-t', '--time', action='store_true',
                        help='print time conversion')
    parser.add_argument('-s', '--snapshot', action='store_true',
                        help='take a camera snapshot to be scanned')
    parser.add_argument('-x', '--test_sequence', action='store_true',
                        help='test_sequence')
    args = parser.parse_args()

    rfm=TextReader(args.basename, args.play)

    # Complete Test sequence with sounds
    if args.test_sequence is True:
        if  args.play is False:
            parser.print_help()
            rfm.close()
            parser.error('Test sequence requires play option. Exiting...')
        print("Test sequence", args.basename)
        test_sequence(rfm)
        rfm.close()
        sys.exit(0)

    # Command line options
    if args.snapshot:
        rfm.reader.snapshot()

    if rfm.reader.is_image() is False:
        parser.print_help()
        print('File: ' + args.basename + '.jpg does not exist. Exiting...')
        sys.exit(1)

    start_time = time.time()
    rfm.reader.ocr_to_text()
    rfm.reader.clean_text()
    rfm.reader.text_to_sound()
    if args.time:
        duration = time.time() - start_time
        print(f"--- Scan: {args.basename+'.jpg'}, Duration: {duration:.2f} seconds ---")

    if args.play:
        rfm.player.play(args.basename+'.wav', blocking=True)

    rfm.close()

if __name__ == '__main__':
    main()
