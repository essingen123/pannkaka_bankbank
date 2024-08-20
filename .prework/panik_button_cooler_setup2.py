#!/usr/bin/env python
import sys
import os
import subprocess

# Set key bindings as variables
TOGGLE_KEY = "<Ctrl><Shift><Alt>space"
DEACTIVATE_KEY = "<Ctrl><Shift><Alt>p"
ACTIVATE_KEY = "<Ctrl><Shift><Alt>o"
# Create the script file
script_path = os.path.expanduser("~/panik_button_cooler.sh")


def list_current_keybindings():
    try:
        print("\nCurrent key bindings:")
        result = subprocess.run(["dconf", "dump", "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/"], capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"\033[91mError listing key bindings: {e}\033[0m")

def the_thing_that_trix_sometimes_holy_grail():
    base_path = "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom"

    shortcuts = [
        {"name": "Panik Button Toggle", "command": f"gnome-terminal -- bash -c '{script_path}'", "key": TOGGLE_KEY, "index": 0},
        {"name": "Panik Button Deactivate", "command": f"gnome-terminal -- bash -c 'rm /tmp/panik_mode && {script_path}'", "key": DEACTIVATE_KEY, "index": 1},
        {"name": "Panik Button Activate", "command": f"gnome-terminal -- bash -c '{script_path}'", "key": ACTIVATE_KEY, "index": 2},
    ]

    for shortcut in shortcuts:
        path = f"{base_path}{shortcut['index']}"
        subprocess.run(["dconf", "write", f"{path}/name", f"'{shortcut['name']}'"], check=True)
        subprocess.run(["dconf", "write", f"{path}/command", f"'{shortcut['command']}'"], check=True)
        subprocess.run(["dconf", "write", f"{path}/binding", f"'{shortcut['key']}'"], check=True)

# Author: Kilian Fun & Cot, 2024
# License+*303%
''' # KEEP THIS ~ IMPORTANT (DO NOT REMOVE:) Note: Works: Issue-fix: dconf with the correct schema + key paths. Keybindning with gsettings couldnt find gsettings didnt find schema /org/gnome/settings-daemon/plugins/media-keys.custom-keybindings after retries. '''
## KEEP THIS WORKING EXAMPLE:  💻$ 
'''

dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/binding "'<Primary><Shift><Alt>t'" && dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/command "'/usr/bin/notify-send HÄJ; '"

dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/binding "'<Primary><Shift><Alt>y'" && dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/command "'/usr/bin/notify-send YESwORKS; '"

dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/binding "'<Primary><Shift><Alt>space'" && dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/command "'/usr/bin/notify-send YESwORKS3; '"

dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/binding "'<Primary><Meta><Alt>space'" && dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/command "'/usr/bin/notify-send hmmDONTknow; '"; 

dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/binding "'<Primary><Alt>space'" && dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/command "'/usr/bin/notify-send nOOOwinkeywoooorks33333; '"; 

dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/binding "'<Primary><Super><Alt>space'" && dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/command "'/usr/bin/notify-send nOOOwinkeywoooorks3477777777444; '"; 

 echo 'meta or super hmm didnt work for windows key, uncertain! '"

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
"""
with open(script_path, "w") as script_file:
    script_file.write(panik_button_script)
# Define the installation script
def install_panik_button():
    try:
        # List current key bindings
        list_current_keybindings()



        # Make the script executable
        subprocess.run(["chmod", "+x", script_path], check=True)

        # Create the bashrc aliases
        bashrc_path = os.path.expanduser("~/.bashrc")
        with open(bashrc_path, "a") as bashrc_file:
            bashrc_file.write("\n# Panik Button Aliases\n")
            bashrc_file.write(f"alias panik='{script_path}'\n")
            bashrc_file.write(f"alias panik_off='rm /tmp/panik_mode && {script_path}'\n")
            bashrc_file.write(f"alias panik_on='{script_path}'\n")

        # Reload the bashrc file
        subprocess.run(["bash", "-c", f"source {bashrc_path}"], check=True)

        # Create the sudoers file
        sudoers_path = "/etc/sudoers.d/panik_button_cooler"
        sudo_command = ["sudo", "bash", "-c", f"echo '%sudo ALL=(ALL) NOPASSWD: {script_path}' > {sudoers_path}"]
        subprocess.run(sudo_command, check=True)

        the_thing_that_trix_sometimes_holy_grail()

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

    except subprocess.CalledProcessError as e:
        print(f"\033[91mError: {e}\033[0m")
    except Exception as e:
        print(f"\033[91mUnexpected error: {e}\033[0m")

# Run the installation script
if __name__ == "__main__":
    install_panik_button()