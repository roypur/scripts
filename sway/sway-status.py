#!/usr/bin/env python3
import subprocess
import os
import json
import datetime
import pydantic
from typing import Final
from pathlib import Path
import socket
import asyncio

SOCKET_PATH: Final[str] = str(Path.home() / ".config/sway-status-vpn.sock")
VPN_STATUS: str = ""


async def start_server() -> None:
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)

    loop = asyncio.get_running_loop()

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    sock.bind(SOCKET_PATH)
    sock.setblocking(False)
    try:
        while True:
            global VPN_STATUS
            VPN_STATUS = (await loop.sock_recv(sock, 128)).decode("utf-8").strip()
    finally:
        try:
            sock.close()
        except Exception:
            pass
        try:
            os.remove(SOCKET_PATH)
        except Exception:
            pass


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

        vpn_prefix: str = f"{VPN_STATUS} "
        if not vpn_prefix.strip():
            vpn_prefix = ""

        next_line = f"{vpn_prefix}{layout} {pretty_time}"
        if battery and battery_status:
            if battery_status == 1:
                next_line = f"{vpn_prefix}{layout} +{battery}% {pretty_time}"
            else:
                next_line = f"{vpn_prefix}{layout} {battery}% {pretty_time}"

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
    print("\nCTRL-C pressed. Terminating")
