# This example demonstrates a UART periperhal.

# This example demonstrates the low-level bluetooth module. For most
# applications, we recommend using the higher-level aioble library which takes
# care of all IRQ handling and connection management. See
# https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble

import bluetooth
import random
import struct
import time
from machine import Pin
from ble_advertising import advertising_payload

from micropython import const

up_button = Pin(2, Pin.IN)
center_button = Pin(3, Pin.IN)
left_button = Pin(4, Pin.IN)
down_button = Pin(5, Pin.IN)
right_button = Pin(6, Pin.IN)

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_READ | _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)


class BLESimplePeripheral:
    #Do not change the name. Appending any number stops the spk-pico from being
    #discoverable. Don't ask me why
    def __init__(self, ble, name="spk-pico"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._connections = set()
        self._write_callback = None
        self._payload = advertising_payload(name=name, services=[_UART_UUID])
        self._advertise()

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("New connection", conn_handle)
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("Disconnected", conn_handle)
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            if value_handle == self._handle_rx and self._write_callback:
                self._write_callback(value)

    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle_tx, data)

    def is_connected(self):
        return len(self._connections) > 0

    def _advertise(self, interval_us=500000):
        print("Starting advertising")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def on_write(self, callback):
        self._write_callback = callback
        
def get_position():
    center_pressed = center_button.value()
    
    if center_pressed:
        if up_button.value():
            return "center-up"
        elif down_button.value():
            return "center-down"
        elif left_button.value():
            return "center-left"
        elif right_button.value():
            return "center-right"
        else:
            return "center"
    else:
        if up_button.value():
            return "up"
        elif down_button.value():
            return "down"
        elif left_button.value():
            return "left"
        elif right_button.value():
            return "right"
        else:
            return "none"
        


def demo():
    ble = bluetooth.BLE()
    p = BLESimplePeripheral(ble)

    def on_rx(v):
        print("RX", v)

    p.on_write(on_rx)
    i = 0
    while True:
        if p.is_connected():
            position = get_position()
            if not position == "none": 
                p.send(position)
                print("Sending position: " + position)
                time.sleep_ms(150)
                position = "none"
                
                
# sudo gatttool -i hci0 -b D8:3A:DD:44:B2:84 -I -t public
if __name__ == "__main__":
    print("Use the following command to interface with the pico from the pi")
    print("Use \"connect\" to establish the connection")
    demo()
