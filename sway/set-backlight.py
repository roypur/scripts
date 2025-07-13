#!/usr/bin/env python3
import sys
import subprocess


def set_brightness(increment: int) -> None:
    result = subprocess.run(
        ["brightnessctl", "get"],
        capture_output=True,
        encoding="utf-8",
    )

    brightness = int(result.stdout.strip())
    brightness += increment

    if brightness < 0:
        brightness = 0

    if brightness > 64764:
        volume = 64764

    subprocess.run(
        [
            "brightnessctl",
            "set",
            str(brightness),
        ],
        capture_output=True,
        encoding="utf-8",
    )


if len(sys.argv) == 2:
    set_brightness(int(sys.argv[1]))
else:
    print(f"{sys.argv[0]} <increment>")
