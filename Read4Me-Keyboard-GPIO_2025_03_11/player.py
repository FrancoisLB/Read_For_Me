import os
import signal

from logger import logger

CMD_PLAY = 'aplay'
CMD_MPLAYER = 'mplayer -slave -idle'


class Player:
    """
    Handle MPlayer process
    """
    def __init__(self):
        """Start MPlayer process"""
        signal.signal(signal.SIGINT, self.handler)
        self.mplayer = os.popen(CMD_MPLAYER, "w")
        self.playing = False

    def play_file(self, basename):
        """Play an audio file using aplay"""
        logger.info('player.speak_file')
        self.playing=True
        outfile = basename+ '.wav'
        cmd = CMD_PLAY + ' ' + outfile
        logger.info("PLAY " + cmd)
        os.system(cmd)
        self.playing=False

    def play_text(self, sentences):
        logger.info('mplayer.play_text')

    def play(self, basename, extension='wav'):
        """
        play an audiofile using MPlayer
        """
        if self.mplayer:
            outfile = basename+ '.' + extension
            self.mplayer.write("stop\n")
            self.mplayer.write("load %s\n" % outfile)
            self.mplayer.flush()

    def pause(self):
        if self.mplayer:
            self.mplayer.write("pause\n")
            self.mplayer.flush()

    def stop(self):
        if self.mplayer:
            self.mplayer.write("stop\n")
            self.mplayer.flush()
            self.playing=False

    def forward(self):
        logger.info('player.forward')
        if self.mplayer:
            self.mplayer.write("seek +10\n")
            self.mplayer.flush()

    def backward(self):
        logger.info('player.backward')
        if self.mplayer:
            self.mplayer.write("seek -10\n")
            self.mplayer.flush()

    def speed_set(self,value):
        if self.mplayer:
            if value < 0 :
                value = 0
            self.mplayer.write("speed_set %f\n" % value)
            self.mplayer.flush()

    def volume_set(self,value):
        if self.mplayer:
            if value < 0 :
                value = 0
            elif value > 100:
                value = 100
            self.mplayer.write("volume %f 1\n" % value)
            self.mplayer.flush()

    def close(self):
        if self.mplayer:
            self.mplayer.write("quit\n")
            self.mplayer.flush()
        self.mplayer = None

    def handler(self, signum, frame):
        msg = "Ctrl-c was pressed. Do you really want to exit? y/n "
        self.close()
        self.stop()
        exit(1)
