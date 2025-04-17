#!/usr/bin/env python3
import time
import evdev

KEYBOARD_NAME = "8BitDo"

CAPABILITIES_KEYBOARD = {
    evdev.ecodes.EV_KEY: [
        evdev.ecodes.KEY_ENTER,
    ],
}

CAPABILITIES_TOUCHSCREEN = {
    evdev.ecodes.EV_KEY: [
        evdev.ecodes.BTN_LEFT,
    ],
    evdev.ecodes.EV_REL: [
        evdev.ecodes.REL_X,
        evdev.ecodes.REL_Y,
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

    with (
        evdev.uinput.UInput(CAPABILITIES_KEYBOARD) as uinput_keyboard,
        evdev.uinput.UInput(CAPABILITIES_TOUCHSCREEN) as uinput_mouse,
    ):
        while True:
            time.sleep(0.05)
            for key in device.active_keys():
                print(key)
                if key == evdev.ecodes.BTN_B:
                    uinput_keyboard.write(
                        evdev.ecodes.EV_KEY, evdev.ecodes.KEY_ENTER, 1
                    )
                    uinput_keyboard.syn()
                    uinput_keyboard.write(
                        evdev.ecodes.EV_KEY, evdev.ecodes.KEY_ENTER, 0
                    )
                    uinput_keyboard.syn()
                if key == evdev.ecodes.BTN_Y:
                    uinput_mouse.write(evdev.ecodes.EV_REL, evdev.ecodes.REL_X, -5000)
                    uinput_mouse.write(evdev.ecodes.EV_REL, evdev.ecodes.REL_Y, -5000)
                    uinput_mouse.syn()
                    time.sleep(1)

                    uinput_mouse.write(evdev.ecodes.EV_REL, evdev.ecodes.REL_X, 1000)
                    uinput_mouse.write(evdev.ecodes.EV_REL, evdev.ecodes.REL_Y, 500)
                    uinput_mouse.syn()
                    time.sleep(0.1)

                    uinput_mouse.write(evdev.ecodes.EV_KEY, evdev.ecodes.BTN_LEFT, 1)
                    uinput_mouse.syn()
                    uinput_mouse.write(evdev.ecodes.EV_KEY, evdev.ecodes.BTN_LEFT, 0)
                    uinput_mouse.syn()


try:
    while True:
        try:
            loop()
        except (SystemError, OSError, KeyError):
            print("8BitDo controller not connected. Retrying")
            time.sleep(1)
except KeyboardInterrupt:
    print()
