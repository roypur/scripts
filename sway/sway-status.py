#!/usr/bin/env python3
import subprocess
import re
import json
import time
import datetime


def get_layout() -> str:
    result = subprocess.run(
        ["swaymsg", "--raw", "--type", "get_inputs"],
        check=True,
        capture_output=True,
        encoding="utf-8",
    )
    for device in json.loads(result.stdout):
        if layout := device.get("xkb_active_layout_name"):
            layout = layout.lower()
            if "english" in layout:
                return "uk"
            elif "norwegian" in layout:
                return "no"
            elif "finnish" in layout:
                return "fi"
            return layout

    return "layout not found"


last_line = ""
while True:
    time.sleep(0.1)
    layout = get_layout()
    ctime = datetime.datetime.now()
    pretty_time = str(
        datetime.datetime(
            day=ctime.day,
            month=ctime.month,
            year=ctime.year,
            hour=ctime.hour,
            minute=ctime.minute,
            second=ctime.second,
        )
    )

    next_line = f"{layout} {pretty_time}"
    if last_line != next_line:
        last_line = next_line
        print(next_line, flush=True)
