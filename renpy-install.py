#!/usr/bin/env python3
import os
import glob
import tempfile
import shutil
import tarfile


def install_engine():
    python_version = 2

    for fname in (
        glob.glob("*.sh", recursive=False)
        + glob.glob("*.py", recursive=False)
        + glob.glob("*.exe", recursive=False)
    ):
        os.remove(fname)

    try:
        os.stat("lib/python2.7")
    except FileNotFoundError:
        python_version = 3

    archive_file = "/home/roypur/Lataukset/renpy-8.2.1-sdk.tar.bz2"
    if python_version == 2:
        archive_file = "/home/roypur/Lataukset/renpy-7.6.2-sdk.tar.bz2"

    with tempfile.TemporaryDirectory() as dirname:
        with tarfile.open(name=archive_file, mode="r:bz2") as archive:
            archive.extractall(path=dirname)
        base = glob.glob(os.path.join(dirname, "renpy-*"))
        shutil.copytree(src=os.path.join(base, "renpy"), dst="renpy")
        shutil.copytree(src=os.path.join(base, "lib"), dst="lib")
        shutil.copyfile(src=os.path.join(base, "renpy.py"), dst="renpy.py")
        shutil.copyfile(src=os.path.join(base, "renpy.sh"), dst="renpy.sh")


try:
    os.stat("renpy")
    os.stat("lib")
    os.stat("game")
except FileNotFoundError:
    print("The current directory is not a renpy game")
else:
    install_engine()
