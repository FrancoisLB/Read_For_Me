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
Key_GPIO class to handle GPIO keypad input
This class provides methods to read input from a GPIO keypad matrix
and trigger corresponding callbacks based on the pressed keys.
"""
import time
from gpiozero import OutputDevice, Button
from constantes import CB
from logger import logger
class KeypadGPIO: # pylint: disable=too-many-instance-attributes
    """
    Key_GPIO class to handle GPIO keypad input
    """
    def __init__(self, dict_callback:dict) -> None:
        """ 
        Initialize the Key_GPIO class.
        
        Parameters:
        -----------
        dict_callback: dict
            A dictionary mapping key values to callback functions.
        """
        self.dict_callback=dict_callback
        self.callbacks=[None]*len(CB)
        # These are the GPIO pin numbers where the lines of the keypad matrix are connected
        self.line1 = 25
        self.line2 = 8
        self.line3 = 7
        self.line4 = 1
        # These are the four columns
        self.col1 = 5
        self.col2 = 6
        self.col3 = 13
        self.col4 = 19
        # The GPIO pin of the column of the key that is currently being
        # held down or -1 if no key is pressed
        self.keypad_pressed = -1
        # Setup GPIO
        # Lines are outputs
        self.line1_out = OutputDevice(self.line1)
        self.line2_out = OutputDevice(self.line2)
        self.line3_out = OutputDevice(self.line3)
        self.line4_out = OutputDevice(self.line4)

        # Columns are inputs with pull-down resistors
        self.col1_in = Button(self.col1, pull_up=False)
        self.col2_in = Button(self.col2, pull_up=False)
        self.col3_in = Button(self.col3, pull_up=False)
        self.col4_in = Button(self.col4, pull_up=False)

        # Detect the rising edges on the column lines of the keypad
        self.col1_in.when_pressed = lambda: self.keypad_callback(self.col1)
        self.col2_in.when_pressed = lambda: self.keypad_callback(self.col2)
        self.col3_in.when_pressed = lambda: self.keypad_callback(self.col3)
        self.col4_in.when_pressed = lambda: self.keypad_callback(self.col4)


    def keypad_callback(self, column:int) -> None:
        """
        Callback function for when a key is pressed.
        This function checks if a key is already pressed and sets 
        the keypad_pressed variable accordingly.
        
        Parameters:
        -----------
        column : int
            The GPIO pin number of the pressed column.
            
        Returns:
        --------
        None
        """
        if self.keypad_pressed == -1:
            self.keypad_pressed = column


    def set_all_lines(self, state:bool)-> None:
        """
        Set all lines to a specific state. This is a helper
        for detecting when the user releases a button
        
        Parameters:
        -----------
        state : bool
            The state to set the lines to (True or False).

        Returns:
        --------
        None
        """
        self.line1_out.value = state
        self.line2_out.value = state
        self.line3_out.value = state
        self.line4_out.value = state


    def read_line(self, line:str, characters:str) -> None:
        """
        Reads the state of a specific line and triggers the corresponding callback
        if a key is pressed.
        Parameters:
        -----------
        line : OutputDevice
            The GPIO pin number of the line to read.
        characters : list
            A list of characters corresponding to the keys in the keypad.
        Returns:
        --------
        None
        """
        line.on()  # Activate the line
        if self.col1_in.is_active:
            print(characters[0])
            self.trigger_callback(int(characters[0]))
        elif self.col2_in.is_active:
            print(characters[1])
            self.trigger_callback(int(characters[1]))
        elif self.col3_in.is_active:
            print(characters[2])
            self.trigger_callback(int(characters[2]))
        elif self.col4_in.is_active:
            print(characters[3])
            self.trigger_callback(int(characters[3]))
        line.off()  # Deactivate the line

    def trigger_callback(self, key:str) -> None:
        """
        Trigger the callback associated with the pressed key.
       
        Parameters:
        -----------
        key : str
            The key that was pressed.
       
        Returns:
        --------
        None
        """
        key = CB(key)
        print("key : ", key)
        if key in self.dict_callback:
            action = int(self.dict_callback[key])
            logger.info("Key %s pressed -> Triggering %s",key, action)
            self.callbacks[action]()

    def start(self):
        """ dummy start function
        """
        print("start")

    def links(self, callbacks:list) -> None:
        """
        Link the GPIO keys to their corresponding callback functions.
        Parameters:
        ----------- 
        callbacks : list
            A list of callback functions to be linked to the keys.
            
        Returns:
        --------
        None    
        """
        self.callbacks = callbacks

        # Link the GPIO keys to their corresponding callback functions
        for key in self.dict_callback:
            callback = callbacks[key.value]
            if callback:
                logger.info("Link GPIO key %s -> %s -> %s", key, self.dict_callback[key], callback)
                self.callbacks[key.value]=callback

    def listen(self):
        """
        Listen for key presses and trigger the corresponding callbacks.
        This function runs in an infinite loop, checking the state of the keys
        and calling the appropriate callback functions when a key is pressed.
        """
        while True:
            # If a button was previously pressed, check whether the user has released it yet
            if self.keypad_pressed != -1:
                self.set_all_lines(True)  # Activate all lines
                if not (self.col1_in.is_active or self.col2_in.is_active
                        or self.col3_in.is_active or self.col4_in.is_active):
                    self.keypad_pressed = -1  # No key is pressed
                else:
                    time.sleep(0.1)
            # Otherwise, just read the input
            else:
                self.read_line(self.line1_out, ["1", "2", "3", "A"])
                self.read_line(self.line2_out, ["4", "5", "6", "B"])
                self.read_line(self.line3_out, ["7", "8", "9", "C"])
                self.read_line(self.line4_out, ["*", "0", "#", "D"])
                time.sleep(0.1)
