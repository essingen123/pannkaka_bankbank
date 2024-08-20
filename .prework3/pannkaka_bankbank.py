#!/usr/bin/env python
import os
import subprocess

# Pannkaka Button Script Content
pannkaka_button_script = """
#!/bin/bash

PANNKAKA_FILE="/tmp/pannkaka_mode"
EXCLUDE_PROCESS_NAMES=("gnome-shell" "pulseaudio" "Xwayland" "cpulimit")
LEVEL_FILE="/tmp/pannkaka_level"

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
            echo "Attempting to limit process: $pid ($cmd) to $level%"
            cpulimit -p $pid -l $level &
        fi
    done <<< "$top_processes"
}

limit_network() {
    echo "💻 Limiting network traffic..."
    # Find the most likely active Wi-Fi interface
    interface=$(ip route show default | awk '/default via/ {print $5}')
    if [[ -n "$interface" ]]; then
        echo "Limiting network interface: $interface"
        sudo tc qdisc add dev "$interface" root handle 1: htb default 12
        sudo tc class add dev "$interface" parent 1: classid 1:1 htb rate $(( 1024 / level ))kbit
        sudo tc class add dev "$interface" parent 1:1 classid 1:12 htb rate $(( 1024 / level ))kbit
    else
        echo "⚠️ No active Wi-Fi interface found. Network limiting may not work."
    fi
}

remove_limits() {
    echo "🔴 Removing CPU and network limits..."
    pkill cpulimit
    # Find the most likely active Wi-Fi interface
    interface=$(ip route show default | awk '/default via/ {print $5}')
    if [[ -n "$interface" ]]; then
        echo "Removing limits from interface: $interface"
        sudo tc qdisc del dev "$interface" root
    fi
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

toggle_pannkaka_mode() {
    if [ -f "$PANNKAKA_FILE" ]; then
        remove_limits
        rm "$PANNKAKA_FILE"
        echo 100 > $LEVEL_FILE
        notify "😴 Pannkaka mode deactivated."
        alert "😴 Pannkaka mode deactivated."
    else
        if [ ! -f "$LEVEL_FILE" ]; then
            echo 50 > $LEVEL_FILE
        fi
        level=$(cat $LEVEL_FILE)
        if [ $level -eq 50 ]; then
            echo 20 > $LEVEL_FILE
        elif [ $level -eq 20 ]; then
            echo 10 > $LEVEL_FILE
        elif [ $level -eq 10 ]; then
            echo 1 > $LEVEL_FILE
        fi
        limit_cpu
        limit_network
        touch "$PANNKAKA_FILE"
        notify "💥 Pannkaka mode activated!"
        alert "💥 Pannkaka mode activated! Level: $(cat $LEVEL_FILE)"
    fi
}

toggle_pannkaka_mode
"""


def run_command(command, input=None):
    try:
        if input is not None:
            subprocess.run(command, check=True, input=input.encode(), shell=True)
        else:
            subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command} (returncode {e.returncode})")


def install_pannkaka_button():
    # --- Diagnostic Commands ---
    print("Diagnostic Information:")
    run_command("whoami")
    run_command("pwd")
    run_command("groups")
    run_command(
        "dconf dump /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/"
    )  # Check existing keybindings

    script_path = os.path.expanduser("~/pannkaka_button_cooler.sh")

    # --- Create and prepare the script ---
    with open(script_path, "w") as script_file:
        script_file.write(pannkaka_button_script)
    run_command(f"chmod +x {script_path}")

    # --- Set up aliases ---
    bashrc_path = os.path.expanduser("~/.bashrc")
    with open(bashrc_path, "a") as bashrc_file:
        bashrc_file.write("\n# Pannkaka Button Aliases\n")
        bashrc_file.write(f"alias pannkaka='{script_path}'\n")
        bashrc_file.write(
            f"alias pannkaka_off='rm /tmp/pannkaka_mode && {script_path}'\n"
        )
        bashrc_file.write(f"alias pannkaka_on='{script_path}'\n")
    run_command(f"bash -c 'source {bashrc_path}'")

    # --- Configure sudoers ---
    sudoers_path = "/etc/sudoers.d/pannkaka_button_cooler"
    run_command(f"sudo rm -f {sudoers_path}")
    run_command(
        f"echo '%sudo ALL=(ALL) NOPASSWD: {script_path}' | sudo tee {sudoers_path}"
    )

    # --- Reset existing keybindings ---
    run_command(
        "dconf reset -f /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/"
    )

    # --- Hardcoded Keybinding Commands ---
    run_command(
        f"dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/binding \"'<Primary><Super><Alt>space'\""
    )
    run_command(
        f"dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/command \"'{script_path}'\""
    )
    run_command(
        f"dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom1/binding \"'<Primary><Super><Alt>p'\""
    )
    run_command(
        f"dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom1/command \"'rm /tmp/pannkaka_mode && {script_path}'\""
    )
    run_command(
        f"dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom2/binding \"'<Primary><Super><Alt>o'\""
    )
    run_command(
        f"dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom2/command \"'{script_path}'\""
    )

    print("\n🎉 Instructions:")
    print("- Press Ctrl+Super+Alt+Space to toggle pannkaka mode. 🥞")
    print("- Press Ctrl+Super+Alt+P to deactivate pannkaka mode. 😴")
    print("- Press Ctrl+Super+Alt+O to activate pannkaka mode. 💥")
    print("- Run 'pannkaka' in the terminal to toggle pannkaka mode. 🤤")
    print("- Run 'pannkaka_off' in the terminal to deactivate pannkaka mode. 🥶")
    print("- Run 'pannkaka_on' in the terminal to activate pannkaka mode. 🔥")


if __name__ == "__main__":
    install_pannkaka_button()
