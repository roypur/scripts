#!/usr/bin/env python3
import time
import evdev

KEYBOARD_NAME = "8BitDo"

CAPABILITIES = {
    evdev.ecodes.EV_KEY: [
        evdev.ecodes.KEY_ENTER,
        evdev.ecodes.BTN_LEFT,
    ],
    evdev.ecodes.EV_REL: [
        evdev.ecodes.REL_X,
        evdev.ecodes.REL_Y,  # Cursor movement
        evdev.ecodes.REL_WHEEL,
        evdev.ecodes.REL_HWHEEL,  # Scroll wheel (optional)
    ],
}


def get_keyboard() -> str:
    for device_name in evdev.list_devices():
        if (
            KEYBOARD_NAME.lower()
            in (device := evdev.InputDevice(device_name)).name.lower()
        ):
            return device
    raise KeyError


def loop() -> None:
    device = get_keyboard()
    device.grab()
    print(device)

    uinput = evdev.uinput.UInput(CAPABILITIES)
    while True:
        time.sleep(0.05)
        for key in device.active_keys():
            if key == evdev.ecodes.BTN_B:
                uinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_ENTER, 1)
                uinput.syn()
                uinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_ENTER, 0)
                uinput.syn()
            if key == evdev.ecodes.BTN_Y:
                uinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.BTN_MOUSE, 1)
                uinput.syn()
                uinput.write(evdev.ecodes.EV_KEY, evdev.ecodes.BTN_MOUSE, 0)
                uinput.syn()


try:
    while True:
        try:
            loop()
        except (SystemError, OSError, KeyError):
            print("8BitDo controller not connected. Retrying")
            time.sleep(1)
except KeyboardInterrupt:
    print()
