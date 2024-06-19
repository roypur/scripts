#!/usr/bin/env python3
import subprocess

with subprocess.Popen(
    [
        "swayidle",
        "-w",
        "timeout",
        "30",
        "swaymsg 'output * dpms off'",
        "resume",
        "swaymsg 'output * dpms on'",
    ]
) as proc:
    subprocess.run(["swaylock"], capture_output=False)
    proc.terminate()
