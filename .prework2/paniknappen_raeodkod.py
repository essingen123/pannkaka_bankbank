#!/usr/bin/env python
import os
import subprocess

# Panic Button Script Content
panic_button_script = """
#!/bin/bash

PANIC_FILE="/tmp/panic_mode"
EXCLUDE_PROCESS_NAMES=("gnome-shell" "pulseaudio" "Xwayland")
LEVEL_FILE="/tmp/panic_level"

limit_cpu() {
    echo "🔥 Limiting CPU usage of top resource-consuming processes..."
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
    echo "💻 Limiting network traffic..."
    sudo tc qdisc add dev eth0 root handle 1: htb default 12
    sudo tc class add dev eth0 parent 1: classid 1:1 htb rate 1mbit
    sudo tc class add dev eth0 parent 1:1 classid 1:12 htb rate 1mbit
}

remove_limits() {
    echo "🔴 Removing CPU and network limits..."
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

toggle_panic_mode() {
    if [ -f "$PANIC_FILE" ]; then
        remove_limits
        rm "$PANIC_FILE"
        notify "😴 Panik mode deactivated."
        alert "😴 Panik mode deactivated."
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
        touch "$PANIC_FILE"
        notify "💥 Panik mode activated!"
        alert "💥 Panik mode activated!"
    fi
}

toggle_panic_mode
"""

# Keybindings
TOGGLE_KEY = "<Ctrl><Super><Alt>space"
DEACTIVATE_KEY = "<Ctrl><Super><Alt>p"
ACTIVATE_KEY = "<Ctrl><Super><Alt>o"


def run_command(command, input=None):
    try:
        subprocess.run(command, check=True, input=input)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command} (returncode {e.returncode})")


def install_panic_button():
    script_path = os.path.expanduser("~/panik_button_cooler.sh")

    # Create the script file
    with open(script_path, "w") as script_file:
        script_file.write(panic_button_script)

    # Make the script executable
    run_command(["chmod", "+x", script_path])

    # Add aliases to .bashrc
    bashrc_path = os.path.expanduser("~/.bashrc")
    with open(bashrc_path, "a") as bashrc_file:
        bashrc_file.write("\n# Panik Button Aliases\n")
        bashrc_file.write(f"alias panik='{script_path}'\n")
        bashrc_file.write(f"alias panik_off='rm /tmp/panic_mode && {script_path}'\n")
        bashrc_file.write(f"alias panik_on='{script_path}'\n")

    # Reload .bashrc
    run_command(["bash", "-c", f"source {bashrc_path}"])

    # Add sudoers entry (CAREFULLY REVIEW THE SCRIPT BEFORE DOING THIS!)
    sudoers_path = "/etc/sudoers.d/panik_button_cooler"
    run_command(
        ["sudo", "tee", sudoers_path],
        input=f"%sudo ALL=(ALL) NOPASSWD: {script_path}\n".encode(),
    )

    # Set up custom keybindings (Gnome specific)
    base_path = (
        "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom"
    )
    shortcuts = [
        {
            "name": "Panik Button Toggle",
            "command": f"gnome-terminal -- bash -c '{script_path}'",
            "key": TOGGLE_KEY,
            "index": 0,
        },
        {
            "name": "Panik Button Deactivate",
            "command": f"gnome-terminal -- bash -c 'rm /tmp/panic_mode && {script_path}'",
            "key": DEACTIVATE_KEY,
            "index": 1,
        },
        {
            "name": "Panik Button Activate",
            "command": f"gnome-terminal -- bash -c '{script_path}'",
            "key": ACTIVATE_KEY,
            "index": 2,
        },
    ]
    for shortcut in shortcuts:
        path = f"{base_path}{shortcut['index']}"
        run_command(["dconf", "write", f"{path}/name", f"'{shortcut['name']}'"])
        run_command(["dconf", "write", f"{path}/command", f'"{shortcut["command"]}"'])
        run_command(["dconf", "write", f"{path}/binding", f"'{shortcut['key']}'"])

    print("\nInstructions:")
    print("- Press Ctrl+Super+Alt+Space to toggle panic mode.")
    print("- Press Ctrl+Super+Alt+P to deactivate panic mode.")
    print("- Press Ctrl+Super+Alt+O to activate panic mode.")
    print("- Run 'panik' in the terminal to toggle panic mode.")
    print("- Run 'panik_off' in the terminal to deactivate panic mode.")
    print("- Run 'panik_on' in the terminal to activate panic mode.")


if __name__ == "__main__":
    install_panic_button()
