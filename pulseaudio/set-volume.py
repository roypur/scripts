#!/usr/bin/env python3
import sys
import subprocess


def get_sink() -> str:
    result = subprocess.run(
        ["pactl", "list", "sinks", "short"],
        capture_output=True,
        encoding="utf-8",
    )
    for line in result.stdout.splitlines():
        sink = line.split()[1]
        if "behringer" in sink.lower():
            return sink
    raise KeyError


def set_volume(increment: int) -> None:
    sink = get_sink()
    result = subprocess.run(
        ["pactl", "get-sink-volume", sink],
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
            sink,
            str(volume),
        ],
        capture_output=True,
        encoding="utf-8",
    )


if len(sys.argv) == 2:
    set_volume(int(sys.argv[1]))
else:
    print(f"{sys.argv[0]} <increment>")
