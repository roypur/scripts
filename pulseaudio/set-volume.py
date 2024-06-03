#!/usr/bin/env python3
import sys
import subprocess


def set_volume(increment: int) -> None:
    result = subprocess.run(
        [
            "pactl",
            "get-sink-volume",
            "alsa_output.usb-BEHRINGER_UMC202HD_192k-00.HiFi__hw_U192k__sink",
        ],
        capture_output=True,
        encoding="utf-8",
    )

    volume = int(result.stdout.split("/")[0].split(":")[-1].strip())
    volume += increment

    if volume < 0:
        volume = 0

    if volume > 65536:
        volume = 65536

    subprocess.run(
        [
            "pactl",
            "set-sink-volume",
            "alsa_output.usb-BEHRINGER_UMC202HD_192k-00.HiFi__hw_U192k__sink",
            str(volume),
        ],
        capture_output=True,
        encoding="utf-8",
    )


if len(sys.argv) == 2:
    set_volume(int(sys.argv[1]))
else:
    print(f"{sys.argv[0]} <increment>")
