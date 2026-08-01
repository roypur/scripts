#!/usr/bin/env python3
import os

term = os.getenv("TERM")
if term not in ["screen", "tmux-256color"]:
    os.execv("/usr/bin/tmux", ["tmux"])
