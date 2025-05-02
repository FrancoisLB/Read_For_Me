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
import time
import subprocess
from logger import logger

class Player:
    """
    Handle MPlayer process
    """
    def __init__(self, volume:int=95, volume_help:int=95, speed:float=1.10):
        """
        Constructor with start MPlayer process
        
        Parameters:
        -----------     
        volume: int
            The volume level to set (0-100)
        volume_help: int
            The volume level for help audio (0-100)
        speed: float    
            The playback speed to set (0-2.0)
        """
        self.cmd_play = 'aplay'
        self.cmd_player = 'mplayer -slave -quiet -idle'
        signal.signal(signal.SIGINT, self.handler)
        # Open a subprocess with mplayer and set it to non-blocking
        self.mplayer = subprocess.Popen(["mplayer", "-slave", "-quiet","-idle"],
                                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        os.set_blocking(self.mplayer.stdout.fileno(), False)
        self.volume = volume
        self.volume_help = volume_help
        self.speed = speed

    def is_playing(self):
        """ Check if MPlayer is playing
        """
        # Get the current position in the audio file
        self.mplayer.stdin.write(b'get_time_pos\n')
        self.mplayer.stdin.flush()
        # Wait for the output
        time.sleep(1)
        # Read the output in non-blocking mode  (last line is the current position)
        first=True
        while True:
            line = self.mplayer.stdout.readline().decode('utf-8')
            if line != '':
                line_prev=line
                if first:
                    first=False
            else:
                if first:
                    output=line.strip()
                else:
                    output=line_prev.strip()
                break
        logger.info('Player.is_playing %s', output)
        return "ANS_TIME_POSITION" in output

    def play(self, audiofile:str, blocking:bool=False) -> None:
        """
        play an audiofile using MPlayer
        
        Parameters:
        -----------
        audiofile: str
            The name of the audio file to play
        blocking: bool
            If True, wait for the audio to finish before returning
            If False, return immediately after starting playback
        
        Returns:
        --------
        None
        """
        logger.info('Player.play')
        if self.mplayer and os.path.exists(audiofile):
            logger.debug('mplayer:play')
            self.mplayer.stdin.write(b"stop\n")
            self.mplayer.stdin.write(bytes(f"load {audiofile}\n", "utf-8"))
            self.mplayer.stdin.flush()
            # Wait for the audio to finish playing
            if blocking:
                time.sleep(5)
                while self.is_playing():
                    time.sleep(5)

    def pause(self) -> None:
        """ Pause the audio playback
        """
        logger.info('Player.pause')
        if self.mplayer:
            logger.debug('mplayer:pause')
            self.mplayer.stdin.write(b'pause\n')
            self.mplayer.stdin.flush()

    def stop(self) -> None:
        """ Stop the audio playback
        """
        logger.info('Player.stop')
        if self.mplayer:
            logger.debug('mplayer:stop')
            self.mplayer.stdin.write(b'stop\n')
            self.mplayer.stdin.flush()

    def forward(self) -> None:
        """ Skip forward in the audio playback
        """
        logger.info('Player.forward')
        if self.mplayer:
            self.mplayer.stdin.write(b'seek +10\n')
            self.mplayer.stdin.flush()

    def backward(self) -> None:
        """ Skip backward in the audio playback
        """
        logger.info('player.backward')
        if self.mplayer:
            self.mplayer.stdin.write(b'seek -10\n')
            self.mplayer.stdin.flush()

    def set_speed(self, value:float) -> None:
        """
        set speed using 
        
        Parameters:
        -----------
        value: float
            The speed value to set (0-2.0)
            
        Returns:
        --------
        None
        """
        logger.info('Player.set_speed')
        if self.mplayer:
            # Ensure the speed is within the range of 0 to 2.0
            # and set it using MPlayer
            value = max(value, 0.0)
            value = min(value, 2.0)
            logger.info('mplayer:set value %f', value)
            self.mplayer.stdin.write(bytes(f"speed_set {value}\n", "utf-8"))
            self.mplayer.stdin.flush()

    def reset_speed(self) -> None:
        """
        reset speed to initial speed value using MPlayer
        """
        logger.info('Player:reset_speed')
        if self.mplayer:
            logger.info('mplayer:reset speed')
            self.mplayer.stdin.write(bytes(f"speed_set {self.speed}\n", "utf-8"))
            self.mplayer.stdin.flush()

    def inc_speed(self) -> None:
        """increase speed with memory
        """
        logger.info('Player:inc_speed')
        if self.mplayer:
            self.speed += 0.1
            self.set_speed(self.speed)

    def dec_speed(self) -> None:
        """
        decrease speed with memory
        """
        logger.info('Player:dec_speed')
        if self.mplayer:
            self.speed -= 0.1
            self.set_speed(self.speed)

    def set_volume(self, value:int) -> None:
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
        logger.info('Player.volume_set %d', value)
        if self.mplayer:
            # Ensure the volume is within the range of 0 to 100
            # and set it using MPlayer
            value = max(value, 0)
            value = min(value, 100)
            logger.debug('mplayer:set volume %d', value)
            self.mplayer.stdin.write(bytes(f"volume {value} 1\n", "utf-8"))
            self.mplayer.stdin.flush()

    def reset_volume(self, help_sound:bool=False) -> None:
        """
        reset volume to initial volume value using MPlayer
        help_sound: bool
            If True, set the volume to the help sound level
            If False, set the volume to the normal level
        """
        logger.info('Player:reset_volume')
        if self.mplayer:
            value = self.volume_help if help_sound else self.volume
            logger.debug('mplayer:set volume %f', value)
            self.mplayer.stdin.write(bytes(f"volume {value} 1\n", "utf-8"))
            self.mplayer.stdin.flush()

    def inc_volume(self) -> None:
        """increase volume with memory
        """
        logger.info('Player:inc_volume')
        if self.mplayer:
            self.volume += 5
            self.set_volume(self.volume)

    def dec_volume(self) -> None:
        """decrease volume with memory
        """
        logger.info('Player:dec_volume')
        if self.mplayer:
            self.volume -= 5
            self.set_volume(self.volume)

    def close(self) -> None:
        """ Close the MPlayer process
        """
        logger.info('Player.close')
        if self.mplayer:
            self.mplayer.stdin.write(b'quit\n')
            self.mplayer.stdin.flush()
        self.mplayer = None

    # pylint: disable=unused-argument
    def handler(self, signum, frame) -> None:
        """ Handle the SIGINT signal (Ctrl-C)
        """
        logger.info('Player:handler Ctrl-c was pressed')
        self.close()
        self.stop()
        sys.exit(1)
