#!/bin/bash
folder=$(mktemp --directory)
mkdir ${folder}/rules
mkdir ${folder}/symbols

curl --silent --output ${folder}/rules/evdev.xml "https://raw.githubusercontent.com/roypur/scripts/master/keyboard/evdev.xml"
curl --silent --output ${folder}/symbols/roypur-no "https://raw.githubusercontent.com/roypur/scripts/master/keyboard/roypur-no"
sudo cp --recursive ${folder}/* /usr/share/X11/xkb

rm -rf ${folder}

echo "Custom keyboard layout installed."
