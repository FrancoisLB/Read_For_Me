"""
    Keypad test code adapted for gpiozero
"""
from logger import logger
from constantes import CB
from gpiozero import OutputDevice, Button
import time

class Key_GPIO:

    def __init__(self, dict_callback):

        self.dict_callback=dict_callback
        self.callbacks=[None]*len(CB)


        # These are the GPIO pin numbers where the lines of the keypad matrix are connected
        self.L1 = 25
        self.L2 = 8
        self.L3 = 7
        self.L4 = 1

        # These are the four columns
        self.C1 = 5
        self.C2 = 6
        self.C3 = 13
        self.C4 = 19

        # The GPIO pin of the column of the key that is currently being held down or -1 if no key is pressed
        self.keypadPressed = -1

        # Setup GPIO
        # Lines are outputs
        self.L1_out = OutputDevice(self.L1)
        self.L2_out = OutputDevice(self.L2)
        self.L3_out = OutputDevice(self.L3)
        self.L4_out = OutputDevice(self.L4)

        # Columns are inputs with pull-down resistors
        self.C1_in = Button(self.C1, pull_up=False)
        self.C2_in = Button(self.C2, pull_up=False)
        self.C3_in = Button(self.C3, pull_up=False)
        self.C4_in = Button(self.C4, pull_up=False)

        # Detect the rising edges on the column lines of the keypad
        self.C1_in.when_pressed = lambda: self.keypadCallback(self.C1)
        self.C2_in.when_pressed = lambda: self.keypadCallback(self.C2)
        self.C3_in.when_pressed = lambda: self.keypadCallback(self.C3)
        self.C4_in.when_pressed = lambda: self.keypadCallback(self.C4)

    # This callback registers the key that was pressed if no other key is currently pressed
    def keypadCallback(self, column):
        if self.keypadPressed == -1:
            self.keypadPressed = column

    # Sets all lines to a specific state. This is a helper for detecting when the user releases a button
    def setAllLines(self, state):
        self.L1_out.value = state
        self.L2_out.value = state
        self.L3_out.value = state
        self.L4_out.value = state

    # Reads the columns and appends the value that corresponds to the button to a variable
    def readLine(self, line, characters):
        line.on()  # Activate the line
        if self.C1_in.is_active:
            print(characters[0])
            self.trigger_callback(int(characters[0]))
        elif self.C2_in.is_active:
            print(characters[1])
            self.trigger_callback(int(characters[1]))
        elif self.C3_in.is_active:
            print(characters[2])
            self.trigger_callback(int(characters[2]))
        elif self.C4_in.is_active:
            print(characters[3])
            self.trigger_callback(int(characters[3]))
        line.off()  # Deactivate the line

    def trigger_callback(self, key):
        """
        Déclenche le callback associé à une touche.
        """
        key = CB(key)
        print("key : ", key)
        if key in self.dict_callback:
            action = int(self.dict_callback[key])
            logger.info(f"Key {key} pressed -> Triggering {action}")
            self.callbacks[action]()  # Appeler le callback

    def start(self):
        print("start")

    def links(self, callbacks):
        """
        Lie les touches du clavier GPIO à des actions (callbacks).
        """
        self.callbacks = callbacks

        # Lier chaque touche du clavier GPIO à une action
        for key in self.dict_callback:
            callback = callbacks[key.value]
            if callback:
                logger.info(f"Link GPIO key {key} -> {self.dict_callback[key]} -> {callback}")
                self.callbacks[key.value]=callback

    def listen(self):
        while True:
            # If a button was previously pressed, check whether the user has released it yet
            if self.keypadPressed != -1:
                self.setAllLines(True)  # Activate all lines
                if not (self.C1_in.is_active or self.C2_in.is_active or self.C3_in.is_active or self.C4_in.is_active):
                    self.keypadPressed = -1  # No key is pressed
                else:
                    time.sleep(0.1)
            # Otherwise, just read the input
            else:
                self.readLine(self.L1_out, ["1", "2", "3", "A"])
                self.readLine(self.L2_out, ["4", "5", "6", "B"])
                self.readLine(self.L3_out, ["7", "8", "9", "C"])
                self.readLine(self.L4_out, ["*", "0", "#", "D"])
                time.sleep(0.1)