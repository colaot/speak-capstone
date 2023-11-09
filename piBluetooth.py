from bluepy import btle
from binascii import hexlify

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        super().__init__()

    def handleNotification(self, cHandle, data):
        text = bytes.fromhex(hexlify(data).decode()).decode('utf-8')
        print("Received data: %s" % text)

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