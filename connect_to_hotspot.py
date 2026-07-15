#!/usr/bin/env python3
import subprocess
import functools
from pick import pick
import time


@functools.cache
def pick_ssid() -> str:
    option, _ = pick(["roypur-hotspot", "roypur"], title="Pick a network")
    return option


def scan_wifi() -> None:
    subprocess.run(["nmcli", "device", "wifi", "rescan"], capture_output=True)


def connect_wifi() -> bool:
    try:
        subprocess.run(
            ["nmcli", "device", "wifi", "connect", pick_ssid()],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        return False
    return True


def connect_loop() -> None:
    while True:
        scan_wifi()
        if connect_wifi():
            print(f"Successfully connected to {pick_ssid()}")
            return
        print(f"Failed to connect to {pick_ssid()}. Trying again.")
        time.sleep(1)


connect_loop()
