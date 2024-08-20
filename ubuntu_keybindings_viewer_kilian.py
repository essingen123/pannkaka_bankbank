#!/usr/bin/env python3
# xpanik_button_cooler_LIST_OTHER_KEYS.py
# -*- coding: utf-8 -*-

import subprocess

def list_current_keybindings():
    try:
        print("\nCurrent key bindings:")
        result = subprocess.run(["dconf", "dump", "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/"], capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"\033[91mError listing key bindings: {e}\033[0m")

if __name__ == "__main__":
    list_current_keybindings()