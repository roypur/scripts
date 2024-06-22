#!/usr/bin/env python3
import subprocess

with subprocess.Popen(
    [
        "swayidle",
        "-w",
        "timeout",
        "5",
        "swaymsg 'output * dpms off'",
        "resume",
        "swaymsg 'output * dpms on'",
    ]
) as proc:
    subprocess.run(["swaylock", "--color", "401e1e"], capture_output=False)
    proc.terminate()
