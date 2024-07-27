#!/usr/bin/env python3
import time
import evdev

KEYBOARD_NAME = "Logitech G815 RGB MECHANICAL GAMING KEYBOARD"


def get_keyboard() -> str:
    for device_name in evdev.list_devices():
        if (device := evdev.InputDevice(device_name)).name == KEYBOARD_NAME:
            return device
    raise KeyError


device = get_keyboard()
print(device)

uinput = evdev.uinput.UInput()
while True:
    time.sleep(0.1)
    for key in device.active_keys():
        if key == evdev.ecodes.KEY_PAUSE:
            uinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_ENTER, 1)
            uinput.syn()
            uinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_ENTER, 0)
            uinput.syn()
