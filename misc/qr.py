#!/usr/bin/env python3
import os.path
import subprocess
import tempfile

with tempfile.TemporaryDirectory() as directory:
    fname = os.path.join(directory, "screenshot.png")
    subprocess.run(
        ["/usr/bin/grim", fname],
        check=True,
        capture_output=True,
        encoding="utf-8",
    )
    try:
        process = subprocess.run(
            ["/usr/bin/zbarimg", "--quiet", fname],
            check=True,
            capture_output=True,
            encoding="utf-8",
        )
        print(process.stdout.strip())
    except subprocess.CalledProcessError:
        print("No QR code found")
