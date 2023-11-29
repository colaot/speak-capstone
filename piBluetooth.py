from bluepy import btle
from binascii import hexlify
import csv

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        super().__init__()
        self.buffer = set() # Buffer to store keys
        self.chordmap = self.init_chords()
        self.chords = [] # Final chord array

    def handleNotification(self, cHandle, data):
        text = bytes.fromhex(hexlify(data).decode()).decode('utf-8')
        print("Received data: %s" % text)

        key, direction, state = self.parse_data(text)

        if state == 'Pressed' and not self.check_buffer_for_key(key, direction):
            self.buffer.add((key, direction, state))
        elif state == 'Released':
            if (key, direction, 'Pressed') in self.buffer:
                self.buffer.discard(key, direction, 'Pressed')
                self.buffer.add(key, direction, state)

        # Check all keys are released
        if self.check_all_keys_released():
            print("Clearing buffer . . .")
            print("Buffer contains:")
            print(self.buffer)
            #above prints needs to be replaced with translate to chars
            #and then from that into chords
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
            if buf_key == key:
                if dir != 'Center' and buf_dir != 'Center':
                    return True
                if dir == 'Center' and buf_dir == 'Center':
                    return True
        return False

    def check_all_keys_released(self):
        for tuple in self.buffer:
            (buf_key, buf_dir, buf_state) = tuple
            if buf_state == 'Pressed':
                return False
        return True

    def parse_data(self, text):
        try:
            key, direction, state = text.strip('()').split(', ')
            return key, direction, state
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
