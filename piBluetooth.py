import pygatt
from binascii import hexlify
import time

adapter = pygatt.GATTToolBackend()

def handle_data(handle, value):
    """
    handle -- integer, characteristic read handle the data was received on
    value -- bytearray, the data returned in the notification
    """
    text = bytes.fromhex(hexlify(value).decode()).decode('utf-8')
    print("Received data: %s" % text)

try:
    adapter.start()
    device = adapter.connect('D8:3A:DD:44:B2:84')

    device.subscribe("6E400003-B5A3-F393-E0A9-E50E24DCCA9E",
                     callback=handle_data)

    # The subscription runs on a background thread. You must stop this main
    # thread from exiting, otherwise you will not receive any messages, and
    # the program will exit. Sleeping in a while loop like this is a simple
    # solution that won't eat up unnecessary CPU, but there are many other
    # ways to handle this in more complicated program. Multi-threaded
    # programming is outside the scope of this README.
    while True:
        time.sleep(10)
finally:
    adapter.stop()