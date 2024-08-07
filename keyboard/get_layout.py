#!/usr/bin/env python3
import subprocess
import json
import re


def main() -> None:
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
                print("uk")
            elif "norwegian" in layout:
                print("no")
            elif "finnish" in layout:
                print("fi")
            return


if __name__ == "__main__":
    main()
