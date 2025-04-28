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
Player class to handle audio playback using MPlayer and aplay
This class provides methods to play, pause, stop, and control the playback
of audio files. It also handles volume and speed adjustments.
It uses the MPlayer command-line interface for playback control
"""
import os
import signal
import sys
from logger import logger

class Player:
    """
    Handle MPlayer process
    """
    def __init__(self):
        """Start MPlayer process
        """
        self.cmd_play = 'aplay'
        self.cmd_player = 'mplayer -slave -quiet -idle'
        signal.signal(signal.SIGINT, self.handler)
        self.mplayer = os.popen(self.cmd_player, "w")
        self.playing = False

    def play_file(self, basename:str) -> None:
        """
        Play an audio file using aplay
            Parameters:
            basename (str): The base name of the audio file to play
    
            Returns:
            None
        """
        logger.info('player.play_file')
        self.playing=True
        outfile = basename+ '.wav'
        cmd = self.cmd_play + ' ' + outfile
        logger.info("PLAY %s ", cmd)
        os.system(cmd)
        self.playing=False


    def play(self, basename:str, extension:str='wav') -> None:
        """
        play an audiofile using MPlayer
        
        Parameters:
        -----------
        basename: str
            The base name of the audio file to play
        extension: str
            The extension of the audio file to play
        
        Returns:
        --------
        None
        """
        logger.info('player.play')
        if self.mplayer:
            outfile = basename+ '.' + extension
            self.mplayer.write("stop\n")
            self.mplayer.write(f"load {outfile}\n")
            self.mplayer.flush()

    def pause(self) -> None:
        """ Pause the audio playback
        """
        logger.info('player.pause')
        if self.mplayer:
            self.mplayer.write("pause\n")
            self.mplayer.flush()

    def stop(self) -> None:
        """ Stop the audio playback
        """
        logger.info('player.stop')
        if self.mplayer:
            self.mplayer.write("stop\n")
            self.mplayer.flush()
            self.playing=False

    def forward(self) -> None:
        """ Skip forward in the audio playback
        """
        logger.info('player.forward')
        if self.mplayer:
            self.mplayer.write("seek +10\n")
            self.mplayer.flush()

    def backward(self) -> None:
        """ Skip backward in the audio playback
        """
        logger.info('player.backward')
        if self.mplayer:
            self.mplayer.write("seek -10\n")
            self.mplayer.flush()

    def speed_set(self, value:float) -> None:
        """ 
        Set the playback speed
        
        Parameters:
        -----------
        value: float
            The speed value to set (0-2.0)
            
        Returns:
        --------
        None
        """
        logger.info('player.speed_set %f', value)
        if self.mplayer:
            # Ensure the speed is within the range of 0 to 2.0
            # and set it using MPlayer
            value = max(value, 0.0)
            value = min(value, 2.0)
            self.mplayer.write(f"speed_set {value}\n")
            self.mplayer.flush()

    def volume_set(self,value:int) -> None:
        """ 
        Set the volume level
        
        Parameters:
        -----------
        value: int
            The volume level to set (0-100)
            
        Returns:
        --------
        None
        """
        logger.info('player.volume_set %d', value)
        if self.mplayer:
            # Ensure the volume is within the range of 0 to 100
            # and set it using MPlayer
            value = max(value, 0)
            value = min(value, 100)
            self.mplayer.write(f"volume {value} 1\n")
            self.mplayer.flush()

    def close(self) -> None:
        """ Close the MPlayer process
        """
        logger.info('player.close')
        if self.mplayer:
            self.mplayer.write("quit\n")
            self.mplayer.flush()
        self.mplayer = None

    # pylint: disable=unused-argument
    def handler(self, signum, frame) -> None:
        """ Handle the SIGINT signal (Ctrl-C)
        """
        logger.info('Player:handler Ctrl-c was pressed')
        self.close()
        self.stop()
        sys.exit(1)
