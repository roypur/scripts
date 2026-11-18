#!/usr/bin/env python3
import pyyaml
from pathlib import PosixPath

def list_profiles() -> list[tuple[str, str]]:
    profile_path = PosixPath("~/.config/librewolf/librewolf/profile.ini").expanduser()
    with open(profile_path, encoding="utf-8") as f:
        print(pyyaml.safe_load(f))

list_profiles()
