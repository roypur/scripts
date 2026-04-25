#!/usr/bin/env python3
import os
import sys

os.execv(
    "/usr/bin/flatpak",
    ["flatpak", "run", "io.gitlab.librewolf-community"] + sys.argv[1:],
)
