from bluepy import btle
from binascii import hexlify
import csv

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        super().__init__()
        self.chordmap = self.init_chords()

    def handleNotification(self, cHandle, data):
        text = bytes.fromhex(hexlify(data).decode()).decode('utf-8')
        print("Received data: %s" % text)
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
