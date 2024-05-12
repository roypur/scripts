#!/usr/bin/env python3
import os
import glob
import tempfile
import shutil
import tarfile


def install_engine():
    python_version = 3 if len(glob.glob("lib/*2.7*", recursive=False)) == 0 else 2

    for fname in (
        glob.glob("*.sh", recursive=False)
        + glob.glob("*.py", recursive=False)
        + glob.glob("*.exe", recursive=False)
    ):
        os.remove(fname)

    shutil.rmtree(path="renpy")
    shutil.rmtree(path="lib")

    archive_file = (
        "/home/roypur/Lataukset/renpy-8.2.1-sdk.tar.bz2"
        if python_version == 3
        else "/home/roypur/Lataukset/renpy-7.6.2-sdk.tar.bz2"
    )

    print(f"Installing {archive_file}")

    with tempfile.TemporaryDirectory() as dirname:
        try:
            with tarfile.open(name=archive_file, mode="r:bz2") as archive:
                archive.extractall(path=dirname)
            base = glob.glob(os.path.join(dirname, "renpy-*"))[0]
            shutil.copytree(src=os.path.join(base, "renpy"), dst="renpy")
            shutil.copytree(src=os.path.join(base, "lib"), dst="lib")
            shutil.copyfile(src=os.path.join(base, "renpy.py"), dst="renpy.py")
            shutil.copyfile(src=os.path.join(base, "renpy.sh"), dst="renpy.sh")
            for dirpath, dirnames, filenames in os.walk("."):
                os.chmod(path=dirpath, mode=0o700)
                for filename in filenames:
                    os.chmod(path=os.path.join(dirpath, filename), mode=0o700)

        except Exception as e:
            print(e)


try:
    os.stat("renpy")
    os.stat("lib")
    os.stat("game")
except FileNotFoundError:
    print("The current directory is not a renpy game")
else:
    install_engine()
