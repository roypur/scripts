#!/usr/bin/env python3
import os
import re
import glob
import tempfile
import shutil
import tarfile
import zipfile
import sys
import secrets


def install_game(game_name: str, archive_name: str, version: str) -> None:
    game_path = os.path.join(os.getcwd(), game_name)
    try:
        os.mkdir(game_path)
    except FileExistsError:
        pass

    output_path = os.path.join(game_path, version)
    if os.path.exists(output_path):
        raise UserWarning(f"Directory already exists {output_path}")

    with tempfile.TemporaryDirectory() as temp_dir:
        extract_path = os.path.join(temp_dir, "extract")
        try:
            os.mkdir(extract_path)
        except FileExistsError:
            pass

        root_dir: str | None = None
        with zipfile.ZipFile(archive_name, "r") as zip_ref:
            for elem in zip_ref.namelist():
                if (cleaned := elem.strip("/")).endswith("/renpy/ast.py"):
                    root_dir = os.path.join(
                        extract_path, cleaned.removesuffix("/renpy/ast.py")
                    )
                    break
            if not root_dir:
                raise UserWarning("This is not a renpy game")
            zip_ref.extractall(extract_path)
        print(f"Extracting game to {output_path}")
        shutil.move(root_dir, output_path)
    os.chdir(output_path)


def install_engine() -> None:
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
        "/home/roypur/Lataukset/renpy-8.5.2-sdk.tar.bz2"
        if python_version == 3
        else "/home/roypur/Lataukset/renpy-7.8.7-sdk.tar.bz2"
    )

    print(f"Installing {archive_file}")

    with tempfile.TemporaryDirectory() as dirname:
        try:
            with tarfile.open(name=archive_file, mode="r:bz2") as archive:
                archive.extractall(path=dirname, filter="tar")
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


def remove_protection() -> None:
    expr = re.compile("def check_load[\\s\\S]+?(?=^def)", flags=re.MULTILINE)
    try:
        with open("renpy/savetoken.py", mode="r", encoding="utf-8") as f:
            code = expr.sub(
                "def check_load(log, signatures):\n    return True\n\n", f.read()
            )
        with open("renpy/savetoken.py", mode="w+", encoding="utf-8") as f:
            f.write(code)
    except Exception as e:
        print(e)


def remove_hard_pause() -> None:
    pause_def = "def pause(delay=None, music=None, with_none=None, hard=False, predict=False, checkpoint=None, modal=None):"
    try:
        with open("renpy/exports/statementexports.py", mode="r", encoding="utf-8") as f:
            code = f.read().replace(
                pause_def,
                pause_def
                + '\n    print("hard={0}".format(bool(hard)))\n    hard = False',
            )
        with open(
            "renpy/exports/statementexports.py", mode="w+", encoding="utf-8"
        ) as f:
            f.write(code)
    except Exception as e:
        print(e)


def main() -> None:
    if len(sys.argv) != 4:
        print(f"{sys.argv[0]} <game_name> <game_version> <archive_name>")
        return

    install_game(game_name=sys.argv[1], version=sys.argv[2], archive_name=sys.argv[3])
    try:
        os.stat("renpy")
        os.stat("lib")
        os.stat("game")
    except FileNotFoundError:
        print("The current directory is not a renpy game")
    else:
        install_engine()
        remove_protection()
        remove_hard_pause()


main()
