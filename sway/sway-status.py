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
            match = re.search("[(](.+)[)]", layout.lower())
            return match.group(1)
    return "layout not found"


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

    print(f"{layout} {pretty_time}")
