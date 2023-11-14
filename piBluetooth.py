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

        if state == 'Pressed':
            self.buffer.add((key, direction))
        elif state == 'Released':
            if (key, direction) in self.buffer:
                self.buffer.remove((key, direction))

        # Check all keys are released
        if not self.buffer:
            self.chords.append(text)
            print("Stored chord: ", text)
            self.buffer.clear()


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
