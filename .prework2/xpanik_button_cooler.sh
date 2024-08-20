#!/bin/bash

panik_FILE="/tmp/panik_mode"
EXCLUDE_PROCESS_NAMES=("gnome-shell" "pulseaudio" "Xwayland")
LEVEL_FILE="/tmp/panik_level"

limit_cpu() {
    echo "Limiting CPU usage of top resource-consuming processes..."
    top_processes=$(ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%cpu | awk 'NR>1 {print $1 " " $4}' | head -n 20)
    level=$(cat $LEVEL_FILE)
    while IFS= read -r line; do
        pid=$(echo $line | awk '{print $1}')
        cmd=$(echo $line | awk '{print $2}')
        exclude=false
        for exclude_name in "${EXCLUDE_PROCESS_NAMES[@]}"; do
            if [[ $cmd == *"$exclude_name"* ]]; then
                exclude=true
                break
            fi
        done
        if [ "$exclude" = false ]; then
            cpulimit -p $pid -l $level &
        fi
    done <<< "$top_processes"
}

limit_network() {
    echo "Limiting network traffic..."
    sudo tc qdisc add dev eth0 root handle 1: htb default 12
    sudo tc class add dev eth0 parent 1: classid 1:1 htb rate 1mbit
    sudo tc class add dev eth0 parent 1:1 classid 1:12 htb rate 1mbit
}

remove_limits() {
    echo "Removing CPU and network limits..."
    pkill cpulimit
    sudo tc qdisc del dev eth0 root
}

notify() {
    notify-send "$1"
    echo "$1"
}

alert() {
    if [ $# -eq 0 ]; then
        notify-send --urgency=low -i "([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e 's/^\\s*[0-9]\\+\\s*//;s/[;&]\\s*alert$//')"
    else
        notify-send --urgency=low -i "terminal" "$*"
    fi
}

toggle_panik_mode() {
    if [ -f "$panik_FILE" ]; then
        remove_limits
        rm "$panik_FILE"
        notify "Panik mode deactivated. Press Ctrl+Meta+Alt+P to pause."
        alert "Panik mode deactivated. Press Ctrl+Meta+Alt+P to pause."
    else
        if [ -f "$LEVEL_FILE" ]; then
            echo 50 > $LEVEL_FILE
        fi
        level=$(cat $LEVEL_FILE)
        if [ $level -eq 50 ]; then
            echo 20 > $LEVEL_FILE
        elif [ $level -eq 20 ]; then
            echo 5 > $LEVEL_FILE
        elif [ $level -eq 5 ]; then
            echo 1 > $LEVEL_FILE
        fi
        limit_cpu
        limit_network
        touch "$panik_FILE"
        notify "Panik mode activated! Press Ctrl+Meta+Alt+O to OMG ON!"
        alert "Panik mode activated! Press Ctrl+Meta+Alt+O to OMG ON!"
    fi
}

toggle_panik_mode