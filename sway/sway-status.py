#!/usr/bin/env python3
from typing import Literal
import subprocess
import os
import json
import datetime
import pydantic
from typing import Final
from pathlib import Path
import socket
import asyncio
import dataclasses

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
    final_vertical_line: bool = True


@dataclasses.dataclass
class NetworkStatus:
    network_type: Literal["wifi", "wired"]
    device: str
    ssid: str


@dataclasses.dataclass
class DefaultRoute:
    ipv4: NetworkStatus | None
    ipv6: NetworkStatus | None


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
                    return "uk | "
                elif "norwegian" in layout:
                    return "no | "
                elif "finnish" in layout:
                    return "fi | "
                return layout
    except Exception:
        pass
    return ""


def get_ssid(uuid: str) -> str | None:
    try:
        result = subprocess.run(
            [
                "nmcli",
                "--terse",
                "--fields",
                "802-11-wireless.ssid",
                "connection",
                "show",
                uuid,
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
        )
        if not (clean_result := result.stdout.strip()).startswith(
            "802-11-wireless.ssid:"
        ):
            return None
        return clean_result.removeprefix("802-11-wireless.ssid:")
    except Exception as e:
        print(e)
    return None


def get_network_status() -> list[NetworkStatus]:
    try:
        result = subprocess.run(
            [
                "nmcli",
                "--terse",
                "--fields",
                "type,device,uuid",
                "connection",
                "show",
                "--active",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
        )
        connections: list[NetworkStatus] = []
        for line in result.stdout.splitlines():
            splitted = line.strip().split(":")
            if len(splitted) == 3:
                if splitted[0] == "802-11-wireless":
                    if ssid := get_ssid(splitted[2]):
                        connections.append(
                            NetworkStatus(
                                network_type="wifi",
                                device=splitted[1],
                                ssid=ssid,
                            )
                        )
                elif splitted[0] == "802-3-ethernet":
                    connections.append(
                        NetworkStatus(
                            network_type="wired",
                            device=splitted[1],
                            ssid="",
                        )
                    )
        return connections
    except Exception:
        pass
    return []


def get_default_route(connections: list[NetworkStatus]) -> DefaultRoute:
    routes = DefaultRoute(ipv4=None, ipv6=None)

    def route_ipv4() -> None:
        try:
            nonlocal routes
            result = subprocess.run(
                ["ip", "-4", "route"],
                check=True,
                capture_output=True,
                encoding="utf-8",
            )
            for line in result.stdout.splitlines():
                splitted = line.split()
                if splitted[0] == "default":
                    for connection in connections:
                        if splitted[4] == connection.device:
                            routes.ipv4 = connection
                            return
        except Exception:
            pass

    def route_ipv6() -> None:
        try:
            nonlocal routes
            result = subprocess.run(
                ["ip", "-6", "route"],
                check=True,
                capture_output=True,
                encoding="utf-8",
            )
            for line in result.stdout.splitlines():
                splitted = line.split()
                if splitted[0] == "default":
                    for connection in connections:
                        if splitted[4] == connection.device:
                            routes.ipv6 = connection
                            return
        except Exception:
            pass

    route_ipv4()
    route_ipv6()
    return routes


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


def network_status_entry() -> str:
    ipv4 = ""
    ipv6 = ""
    route_all = ""
    default_route = get_default_route(get_network_status())
    if default_route.ipv4 is not None and default_route.ipv4 == default_route.ipv6:
        if default_route.ipv4.network_type == "wifi":
            route_all = (
                f"[v4,v6:{default_route.ipv4.network_type}][{default_route.ipv4.ssid}]"
            )
        else:
            route_all = f"[v4,v6:{default_route.ipv4.network_type}]"
    else:
        if default_route.ipv4 is not None:
            if default_route.ipv4.network_type == "wifi":
                ipv4 = (
                    f"[v4:{default_route.ipv4.network_type}][{default_route.ipv4.ssid}]"
                )
            else:
                ipv4 = f"[v4:{default_route.ipv4.network_type}]"
        if default_route.ipv6 is not None:
            if default_route.ipv6.network_type == "wifi":
                ipv6 = (
                    f"[v6:{default_route.ipv6.network_type}][{default_route.ipv6.ssid}]"
                )
            else:
                ipv6 = f"[v6:{default_route.ipv6.network_type}]"
    if route_all:
        return f"{route_all} | "
    if ipv4 and ipv6:
        return f"{ipv4} | {ipv6} | "
    if ipv4:
        return f"{ipv4} | "
    if ipv6:
        return f"{ipv6} | "
    return ""


async def start_loop() -> None:
    last_line = ""
    while True:
        await asyncio.sleep(0.1)
        network_status = network_status_entry()

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

        vpn_prefix: str = ""
        if trimmed_vpn_status := VPN_STATUS.strip():
            vpn_prefix = f"{trimmed_vpn_status} | "

        battery_entry = ""
        if battery:
            battery_entry = f"{battery}% | "
            if battery_status == 1:
                battery_entry = f"+{battery}% | "

        terminator = ""
        if CONFIG_FILE.final_vertical_line:
            terminator = " | "

        next_line = f"| {network_status}{vpn_prefix}{layout}{battery_entry}{pretty_time}{terminator}"
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
