#!/usr/bin/env python3
import subprocess
import re
import json
import time
import datetime
from pathlib import Path


class ConfigFile(pydantic.BaseModel):
    battery_capacity_file: str = "/sys/class/power_supply/BAT0/capacity"
    battery_status_file: str = "/sys/class/power_supply/BAT0/status"


def get_config() -> ConfigFile:
    try:
        with open(
            Path.home() / ".config/sway-status.json", mode="r", encoding="utf-8"
        ) as f:
            return ConfigFile.model_validate(json.loads(f.read()))
    except FileNotFoundError:
        with open(
            Path.home() / ".config/sway-status.json", mode="x", encoding="utf-8"
        ) as f:
            config = ConfigFile()
            f.write(config.model_dump_json(exclude_none=False, indent=4))
            return config


def get_layout() -> str:
    try:
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
    except Exception:
        pass
    return "layout not found"


def read_battery(config: ConfigFile) -> int:
    try:
        with open(config.battery_capacity_file, encoding="utf-8") as f:
            return int(f.read())
    except Exception:
        pass
    return 0


def read_battery_status(config: ConfigFile) -> int:
    try:
        with open(config.battery_capacity_file, encoding="utf-8") as f:
            status = f.read().lower().strip()
            if status == "discharging":
                return -1
            if status == "not charging":
                return 1
            if status == "charging":
                return 1
    except Exception:
        pass
    return 0


last_line = ""
while True:
    time.sleep(0.1)
    config = get_config()
    layout = get_layout()
    battery = read_battery(config)
    battery_status = read_battery_status(config)

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
    if battery and battery_status:
        if battery_status == 1:
            next_line = f"{layout} +{battery}% {pretty_time}"
        else:
            next_line = f"{layout} {battery}% {pretty_time}"

    if last_line != next_line:
        last_line = next_line
        print(next_line, flush=True)
