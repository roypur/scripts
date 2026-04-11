#!/usr/bin/env python3
import subprocess
import os
import re
import json
import time
import datetime
import pydantic
from typing import Final
from pathlib import Path
import asyncio

SOCKET_PATH: Final[str] = str(Path.home() / ".config/sway-status-vpn.sock")


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


CONFIG_FILE: Final[ConfigFile] = get_config()
VPN_STATUS: str = ""


async def handle_client(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    global VPN_STATUS
    VPN_STATUS = (await reader.read(128)).decode("utf-8")

    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def start_server() -> None:
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    server = await asyncio.start_unix_server(handle_client, path=SOCKET_PATH)

    async with server:
        await server.serve_forever()


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


def read_battery() -> int:
    try:
        with open(CONFIG_FILE.battery_capacity_file, encoding="utf-8") as f:
            return int(f.read())
    except Exception:
        pass
    return 0


def read_battery_status() -> int:
    try:
        with open(CONFIG_FILE.battery_status_file, encoding="utf-8") as f:
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


async def start_loop() -> None:
    last_line = ""
    while True:
        await asyncio.sleep(0.1)
        layout = get_layout()
        battery = read_battery()
        battery_status = read_battery_status()

        ctime = datetime.datetime.now(tz=datetime.UTC).astimezone()
        pretty_time = datetime.datetime(
            day=ctime.day,
            month=ctime.month,
            year=ctime.year,
            hour=ctime.hour,
            minute=ctime.minute,
            second=ctime.second,
            tzinfo=ctime.tzinfo,
        ).isoformat()

        next_line = f"{layout} {pretty_time}"
        if battery and battery_status:
            if battery_status == 1:
                next_line = f"{layout} +{battery}% {pretty_time}"
            else:
                next_line = f"{layout} {battery}% {pretty_time}"

        if last_line != next_line:
            last_line = next_line
            print(next_line, flush=True)


async def main() -> None:
    try:
        unix_socket_task = asyncio.create_task(start_server())
        loop_task = asyncio.create_task(start_loop())
        await asyncio.gather(unix_socket_task, loop_task)
    except KeyboardInterrupt:
        print("CTRL-C pressed. Terminating")


try:
    asyncio.run(main())
except KeyboardInterrupt:
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)
    print("\nCTRL-C pressed. Terminating")
