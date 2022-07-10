#!/usr/bin/env python3
import urllib.parse
import requests

mirrors: dict[int, list[str]] = {}
scores: list[int] = []

resp = requests.get("https://archlinux.org/mirrors/status/json/")

for mirror in resp.json().get("urls"):
    if not (
        mirror.get("protocol") == "https"
        and mirror.get("ipv4")
        and mirror.get("ipv6")
        and mirror.get("score")
        and mirror.get("url")
        and mirror.get("country_code")
    ):
        continue
    pos = int(mirror.get("score") * 100)
    if not mirrors.get(pos):
        mirrors[pos] = []
        scores.append(pos)
    mirrors[pos].append(
        "Server = " + urllib.parse.urljoin(mirror.get("url"), "$repo/os/$arch")
    )

scores.sort()

formatted = ""
for score in scores:
    for mirror in mirrors[score]:
        formatted += f"{mirror}\n"

with open(file="/etc/pacman.d/mirrorlist", mode="w", encoding="UTF-8") as f:
    f.write(formatted)
