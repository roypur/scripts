#!/usr/bin/env python3
import subprocess
import json
from pathlib import Path
from typing import Final
import pydantic


class ConfigFile(pydantic.BaseModel):
    dpms_timeout: int = 5


def get_config() -> ConfigFile:
    try:
        with open(
            Path.home() / ".config/sway-lock-with-dpms.json", mode="r", encoding="utf-8"
        ) as f:
            return ConfigFile.model_validate(json.loads(f.read()))
    except FileNotFoundError:
        with open(
            Path.home() / ".config/sway-lock-with-dpms.json", mode="x", encoding="utf-8"
        ) as f:
            config = ConfigFile()
            f.write(config.model_dump_json(exclude_none=False, indent=4))
            return config


CONFIG_FILE: Final[ConfigFile] = get_config()


with subprocess.Popen(
    [
        "swayidle",
        "-w",
        "timeout",
        str(CONFIG_FILE.dpms_timeout),
        "swaymsg 'output * dpms off'",
        "resume",
        "swaymsg 'output * dpms on'",
    ]
) as proc:
    subprocess.run(["swaylock", "--color", "401e1e"], capture_output=False)
    proc.terminate()
