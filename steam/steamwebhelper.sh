#!/usr/bin/env bash
dir=$(dirname $(realpath $0))
export LD_LIBRARY_PATH="/usr/lib64:/usr/lib32:/usr/lib64/libva1:/usr/lib32/libva1:${LD_LIBRARY_PATH}:${dir}"
cd "${dir}"

./steamwebhelper "$@"
