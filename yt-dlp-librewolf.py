#!/usr/bin/env python3
import configparser
from pathlib import PosixPath
import os
import sys
import json
import copy


def list_profiles() -> dict[str, str]:
    profiles: dict[str, str] = {}
    config = configparser.ConfigParser()
    config.read(PosixPath("~/.config/librewolf/librewolf/profiles.ini").expanduser())
    for section, body in config.items():
        if (
            section.startswith("Profile")
            and (name := body.get("Name")) is not None
            and (path := body.get("Path")) is not None
        ):
            profile_path = str(
                PosixPath("~/.config/librewolf/librewolf").expanduser() / path
            )
            profiles[name] = f"firefox:{profile_path}"

    return profiles


def profile_path(profile_name: str) -> str:
    profiles = list_profiles()
    if (profile := profiles.get(profile_name)) is not None:
        return profile
    print("-" * 20)
    print(f"Selected profile not found: {profile_name}")
    print("See available profiles below:")
    print(json.dumps(profiles, indent=4))
    print("-" * 20)
    raise KeyError("Profile not found")


def main() -> None:
    if len(sys.argv) >= 2:
        try:
            selected_profile = profile_path(sys.argv[1])
        except KeyError:
            return
        base_command = ["yt-dlp", "--cookies-from-browser", selected_profile]
        extra = copy.deepcopy(sys.argv)
        extra.pop(0)
        extra.pop(0)
        os.execvp("yt-dlp", base_command + extra)
    print(f"{sys.argv[0]} <profile> <yt_dlp_commands>")


if __name__ == "__main__":
    main()
