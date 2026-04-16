#!/usr/bin/env python3
import argparse
from typing import Final
import os
import tempfile
import subprocess
from pathlib import Path

PUBKEY_PATH: Final[str] = str(Path(__file__).resolve().parent / "pubkey.asc")
FINGERPRINT: Final[str] = "21A8AFA8685FE17AEE409069D30DE5E96E4B9002"


def encrypt_file(file: str) -> None:
    with tempfile.TemporaryDirectory() as gnupg_home:
        env = os.environ.copy()
        env["GNUPGHOME"] = gnupg_home
        subprocess.run(
            ["gpg", "--import", PUBKEY_PATH],
            check=True,
            capture_output=True,
            env=env,
            encoding="utf-8",
        )
        subprocess.run(
            [
                "gpg",
                "--encrypt",
                "--batch",
                "--yes",
                "--trust-model",
                "always",
                "--armor",
                "--recipient",
                FINGERPRINT,
                file,
            ],
            check=True,
            capture_output=False,
            env=env,
            encoding="utf-8",
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, required=True)
    args = parser.parse_args()
    encrypt_file(file=args.file)


if __name__ == "__main__":
    main()
