#!/usr/bin/env python
import sys
import os
import subprocess

script_path = os.path.join(os.path.dirname(__file__), "xpanik_button_cooler.sh")

TOGGLE_KEY = "\"'<Primary><Super><Alt>space'\""
DEACTIVATE_KEY = "\"'<Primary><Super><Alt>p'\""
ACTIVATE_KEY = "\"'<Primary><Super><Alt>o'\""


def install_panik_button():
    try:
        # Set up custom keybindings (Gnome specific)
        subprocess.run(
            f"dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/binding {TOGGLE_KEY} && dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/command '/usr/bin/notify-send 111; {script_path}'",
            shell=True
        )
        subprocess.run(
            f"dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom1/binding {DEACTIVATE_KEY} && dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom1/command '/usr/bin/notify-send DeactivatePanikMode; rm /tmp/panik_mode && {script_path}'",
            shell=True
        )
        subprocess.run(
            f"dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom2/binding {ACTIVATE_KEY} && dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom2/command '/usr/bin/notify-send ActivatePanikMode; {script_path}'",
            shell=True
        )

        # Set up script permissions
        subprocess.run(["chmod", "+x", script_path], check=True)

        # Add aliases to .bashrc
        bashrc_path = os.path.expanduser("~/.bashrc")
        with open(bashrc_path, "a") as bashrc_file:
            bashrc_file.write("\n# Panik Button Aliases\n")
            bashrc_file.write(f"alias panik='{script_path}'\n")
            bashrc_file.write(
                f"alias panik_off='rm /tmp/panik_mode && {script_path}'\n"
            )
            bashrc_file.write(f"alias panik_on='{script_path}'\n")

        # Reload .bashrc
        subprocess.run(["bash", "-c", f"source {bashrc_path}"], check=True)

        # Add sudoers entry (CAREFULLY REVIEW THE SCRIPT BEFORE DOING THIS!)
        sudoers_path = "/etc/sudoers.d/panik_button_cooler"
        sudo_command = [
            "sudo",
            "bash",
            "-c",
            f"echo '%sudo ALL=(ALL) NOPASSWD: {script_path}' > {sudoers_path}",
        ]
        subprocess.run(sudo_command, check=True)

        print("\nInstructions:")
        print("- Press <Primary><Super><Alt>space to toggle panic mode.")
        print("- Press <Primary><Super><Alt>p to deactivate panic mode.")
        print("- Press <Primary><Super><Alt>o to activate panic mode.")
        print("- Run 'panik' in the terminal to toggle panic mode.")
        print("- Run 'panik_off' in the terminal to deactivate panic mode.")
        print("- Run 'panik_on' in the terminal to activate panic mode.")

    except subprocess.CalledProcessError as e:
        print(
            f"\033[91mError: Command failed with return code {e.returncode}. Output: {e.output}\033[0m"
        )
    except Exception as e:
        print(f"\033[91mUnexpected error: {e}\033[0m")


if __name__ == "__main__":
    install_panik_button()
