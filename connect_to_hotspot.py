#!/usr/bin/env python3
import subprocess
import time

HOTSPOT_NAME = "roypur-hotspot"


def scan_wifi() -> None:
    subprocess.run(["nmcli", "device", "wifi", "rescan"], capture_output=True)


def connect_wifi() -> bool:
    try:
        subprocess.run(
            ["nmcli", "device", "wifi", "connect", HOTSPOT_NAME],
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
            print(f"Successfully connected to {HOTSPOT_NAME}")
            return
        print(f"Failed to connect to {HOTSPOT_NAME}. Trying again.")
        time.sleep(1)


connect_loop()
