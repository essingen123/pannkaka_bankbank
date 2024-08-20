#!/usr/bin/env python
import sys
import os
import subprocess

# Author:  Kilian Fun & Cot, 2024
# License+*303%
''' # KEEP THIS ~ IMPORTANT (DO NOT REMOVE:) Note: Using dconf instead of gsettings to set custom keybindings: The schema /org/gnome/settings-daemon/plugins/media-keys.custom-keybindings was not found when using gsettings Switching to dconf and using the correct schema and key paths fixed the issue'''
## KEEP THIS; IT WORKS!! : koji@kojiasus:koji(240819 18:33:42)💻$ dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/binding "'<Primary><Shift><Alt>t'" && dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/command "'/usr/bin/notify-send HÄJ'"


# Set key bindings as variables
TOGGLE_KEY = "'<Ctrl><Shift><Alt>space'"
DEACTIVATE_KEY = "'<Ctrl><Shift><Alt>p'"
ACTIVATE_KEY = "'<Ctrl><Shift><Alt>o'"
# not meta or super for the windows button?????? the left one????

# Define the script to be installed
panik_button_script = """
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
    sudo -i tc qdisc add dev eth0 root handle 1: htb default 12
    sudo -i tc class add dev eth0 parent 1: classid 1:1 htb rate 1mbit
    sudo -i tc class add dev eth0 parent 1:1 classid 1:12 htb rate 1mbit
}

remove_limits() {
    echo "Removing CPU and network limits..."
    pkill cpulimit
    sudo -i tc qdisc del dev eth0 root
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
"""

# Define the installation script
def install_panik_button():
    # Create the script file
    script_path = os.path.expanduser("~/panik_button_cooler.sh")
    with open(script_path, "w") as script_file:
        script_file.write(panik_button_script)

    # Make the script executable
    subprocess.run(["chmod", "+x", script_path])

    # Create the bashrc aliases
    bashrc_path = os.path.expanduser("~/.bashrc")
    with open(bashrc_path, "a") as bashrc_file:
        bashrc_file.write("\n# Panik Button Aliases\n")
        bashrc_file.write(f"alias panik='{script_path}'\n")
        bashrc_file.write(f"alias panik_off='rm /tmp/panik_mode && {script_path}'\n")
        bashrc_file.write(f"alias panik_on='{script_path}'\n")

    # Reload the bashrc file
    subprocess.run(["bash", "-c", f"source {bashrc_path}"])

    # Create the sudoers file
    sudoers_path = "/etc/sudoers.d/panik_button_cooler"
    sudo_command = ["sudo", "-i", "bash", "-c", f"echo '%sudo   ALL=(ALL) NOPASSWD: {script_path}' > {sudoers_path}"]
    subprocess.run(sudo_command)

    base_path = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom"

    shortcuts = [
        {"name": "Panik Button Toggle", "command": f"gnome-terminal -- bash -c '{script_path}'", "key": TOGGLE_KEY, "index": 0},
        {"name": "Panik Button Deactivate", "command": f"gnome-terminal -- bash -c 'rm /tmp/panik_mode && {script_path}'", "key": DEACTIVATE_KEY, "index": 1},
        {"name": "Panik Button Activate", "command": f"gnome-terminal -- bash -c '{script_path}'", "key": ACTIVATE_KEY, "index": 2},
    ]

    for shortcut in shortcuts:
        path = f"{base_path}{shortcut['index']}"
        subprocess.run(["dconf", "write", f"{path}/name", f"'{shortcut['name']}'"])
        subprocess.run(["dconf", "write", f"{path}/command", f"'{shortcut['command']}'"])
        subprocess.run(["dconf", "write", f"{path}/binding", shortcut['key']])
    # Print the final message
    print("\nFinal message with instructions:")
    instructions = [
        f"Press {TOGGLE_KEY} to toggle panik mode.",
        f"Press {DEACTIVATE_KEY} to deactivate panik mode.",
        f"Press {ACTIVATE_KEY} to activate panik mode.",
        "Run 'panik' in the terminal to toggle panik mode.",
        "Run 'panik_off' in the terminal to deactivate panik mode.",
        "Run 'panik_on' in the terminal to activate panik mode.",
        "Enjoy your panik button!"
    ]

    for instruction in instructions:
        print(f"\033[92m{instruction}\033[0m")

# Run the installation script
install_panik_button()