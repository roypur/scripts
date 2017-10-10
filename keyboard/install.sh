#!/bin/bash
sudo bash --command << EOF
wget -O /usr/share/X11/xkb/rules/evdev.xml 
wget -O /usr/share/X11/xkb/symbols/roypur-no
EOF
