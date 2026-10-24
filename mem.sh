#!/usr/bin/env bash

pid=$(pgrep -n -x renpy)
cg=$(awk -F: '$1 == "0" {print $3}' "/proc/$pid/cgroup")
d="/sys/fs/cgroup$cg"

while [ -r "$d/memory.current" ]; do
    echo "===== $(date +%T) ====="
    echo "Cgroup: $cg"
    echo "Memory current:"
    cat "$d/memory.current"

    echo "Memory breakdown:"
    grep -E '^(anon|file|shmem|kernel|kernel_stack|pagetables|sock|slab) ' \
        "$d/memory.stat"

    echo "Processes in this cgroup and descendants:"
    find "$d" -name cgroup.procs -type f -exec cat {} + 2>/dev/null |
        sort -nu |
        while read -r p; do
            [ -r "/proc/$p/status" ] || continue
            awk -v p="$p" '
                /^Name:/ { name=$2 }
                /^VmRSS:/ { rss=$2 }
                /^VmSize:/ { vsz=$2 }
                END {
                    printf "PID=%s RSS=%s kB VSZ=%s kB NAME=%s\n",
                        p, rss, vsz, name
                }
            ' "/proc/$p/status"
        done

    sleep 3
done
