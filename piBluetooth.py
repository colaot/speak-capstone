from bluepy import btle
from binascii import hexlify
import csv

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        super().__init__()
        self.buffer = [] # Buffer to store keys
        # self.chordmap = self.init_chords()
        self.chords = [] # Final chord array

# Up, Right, Down, Left, Center :: 0, 1, 2, 3, 4
# Pressed, Released :: 1, 0

    def handleNotification(self, cHandle, data):
        text = bytes.fromhex(hexlify(data).decode()).decode('utf-8')
        print("Received data: %s" % text)

        key, direction, state = self.parse_data(text)
        if state == 1 and not self.check_buffer_for_key(key, direction):
            self.buffer.append((key, direction, state))
        elif state == 0:
            if (key, direction, 1) in self.buffer:
                self.buffer.remove((key, direction, 1))
                self.buffer.append((key, direction, state))

        # Check all keys are released
        if self.check_all_keys_released():
            print("Buffer contains:")
            print(self.buffer)
            print(self.translate_to_chars())
            #above prints needs to be replaced with translate to chars
            #and then from that into chords
            print("Clearing buffer . . .")
            self.buffer.clear()

    #checks if key (int) already exists in buffer
    def check_buffer_for_key(self, key, dir):
        for tuple in self.buffer:
            #unpacks tuple
            (buf_key, buf_dir, buf_state) = tuple
            # case 1: key is same neither new or old are center: True
            # case 2: key is same old is center, new is not: False
            # case 3: key is same new is center, old is not: False
            # case 4: key is same both center: True
            # case 5: keys not the same: False

            #THIS HURTS ABILITY TO SOLO CENTER PRESS, NEED FIX
            if buf_key == key:
                if dir != 4 and buf_dir != 4:
                    return True
                if dir == 4 and buf_dir == 4:
                    return True
        return False

    def check_all_keys_released(self):
        if len(self.buffer) == 0:
            return False
        for tuple in self.buffer:
            (buf_key, buf_dir, buf_state) = tuple
            if buf_state == 1:
                return False
        return True

    def translate_to_chars(self):
        tuple_buf = []
        char_buf = []
        char_dict = self.init_char_map()
        # check each key for a center and other press
        for tuple in self.buffer:
            (buf_key, buf_dir, buf_state) = tuple
            if (buf_dir != 4):
                # if keystroke is not center press, check for corresponding center press
                if self.center_press_in_buf(buf_key):
                    tuple_buf.append((buf_key, buf_dir, 1))
                else:
                    tuple_buf.append((buf_key, buf_dir, 0))
            else:
                # if keystroke is center press, check for corresponding non-center press
                if not self.non_center_press_in_buf(buf_key):
                    tuple_buf.append((buf_key, buf_dir, 0))
        for tuple in tuple_buf:
            char_buf.append(char_dict.get(tuple))
        return char_buf

    def center_press_in_buf(self, key):
        for tuple in self.buffer:
            (buf_key, buf_dir, buf_state) = tuple
            if (buf_dir == 4 and buf_key == key):
                return True
        return False

    def non_center_press_in_buf(self, key):
            for tuple in self.buffer:
                (buf_key, buf_dir, buf_state) = tuple
                if (buf_dir != 4 and buf_key == key):
                    return True
            return False

    def init_char_map(self):
        with open('press_to_char.csv', newline = '') as csvfile:
            reader = csv.DictReader(csvfile)
            tuple = []
            chars = []
            for row in reader:
                tuple.append((int(row["KEY"]), int(row["DIRECTION"]), int(row["CENTER"])))
                chars.append(row["CHAR"])
        return {tuple[i]:chars[i] for i in range(len(tuple))}


    def parse_data(self, text):
        try:
            key, direction, state = text.strip('()').split(', ')
            return int(key), int(direction), int(state)
        except ValueError:
            print("Invalid data format")
            return None, None, None

''' commented out for later development
        if(text in self.chordmap) :
            print(self.chordmap.get(text))
        else:
            print("Not a chord")


    def init_chords(self):
        with open('chords.csv', newline = '') as csvfile:
            reader = csv.DictReader(csvfile)
            keys = []
            vals = []
            for row in reader:
                key.append(row["CHORD"])
                key.append(row["WORD"])
        return {keys[i]:vals[i] for i in range (len(keys))}

'''

pico_mac_address = 'D8:3A:DD:44:B2:84'
characteristic_uuid = '6e400003-b5a3-f393-e0a9-e50e24dcca9e'

p = btle.Peripheral(pico_mac_address)
p.setDelegate(MyDelegate())

try:
    while True:
        if p.waitForNotifications(1.0):
            continue
        print("Waiting for notifications...")
except btle.BTLEDisconnectError:
    print("The device has disconnected")
except KeyboardInterrupt:
    print("Script interrupted by the user")
finally:
    p.disconnect()
