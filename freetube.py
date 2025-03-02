#!/usr/bin/env python3
import os
import sys
import glob
from pathlib import Path
import re
from packaging.version import Version

base_dir = os.path.join(str(Path.home()), "development/FreeTube/build")

command = ["FreeTube"]


builds = glob.glob(os.path.join(base_dir, "FreeTube-*.AppImage"))


def compare(elem: dict) -> Version:
    return elem["version"]


def main() -> None:
    versions = []
    for build in builds:
        if (current_match := re.findall("FreeTube-([0-9.]+)\\.AppImage", build)) and (
            current_match[0] not in versions
        ):
            versions.append({"fname": build, "version": Version(current_match[0])})

    if not versions:
        print("No versions found")

    latest = sorted(versions, key=compare, reverse=True)[0]
    os.execv(os.path.join(base_dir, latest["fname"]), command)


main()
