#!/usr/bin/env python
# ubuntu_keybindings_editor.py
# -*- coding: utf-8 -*-

import subprocess
import os
import time

# Blinking caveat
print("\033[91m✨❗️ CAVEAT CARROT CARE ❗️✨\033[0m")
print(" ⚠️ Edit keybindings !")
time.sleep(1)  # Blinking effect


# Author and license information
print("\n✨ Author: Kilian Fun Der Kind &&")
print(" Cotelligence 2024 ✨")
print(" License: MIT+*303% ✨")

# Disclaimer
print("\n✨ DISCLAIMER ✨")
print(" Only intended to be used by bananas 🍌")

# Serious information
print("\n✨ Script Requirements ✨")
print(" This script is designed to work on any Ubuntu version")
print(" that uses the GNOME desktop environment, including:")
print(" Ubuntu 22.04 (GNOME 42), Ubuntu 21.10 (GNOME 41),")
print(" Ubuntu 21.04 (GNOME 40), and Ubuntu 20.04 LTS (GNOME 3.36)")
print(" The script uses the dconf command and nano text editor.")
print(" Make sure they are installed and available in your system.")

# Information about the script
print("\n✨ Ubuntu Keybindings Editor ✨")
print(" List, delete, and edit custom keybindings in Ubuntu like never before.")

# Sponsor advertisement
print("\n*******SPONSOR ADVERTISEMENT MESSAGE VIA TERMINAL AD NETWORK INTERGALACTIC****")
print(" Looking for your next Romantic")
print(" Terminal Travel Experience? Ofcourse you are. 🏔️")
print(" ☀️🌳 Explore the majestic")
print(" tree. Book your Travel With a terminal")
print(" Experience lovely moments etc")
print(" ❤️❤️❤️ 🚀❤️❤️❤️❤️")


def list_keybindings():
    try:
        result = subprocess.run(["dconf", "dump", "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/"], capture_output=True, text=True, check=True)
        keybindings = result.stdout.strip().splitlines()
        id = 1
        print("\n✨❤️ Current key bindings: ❤️✨")
        for i in range(0, len(keybindings), 4):
            print(f"KB{id}:")
            for j in range(4):
                print(f"  {keybindings[i+j]}")
            id += 1
    except subprocess.CalledProcessError as e:
        print(f"\033[91m❗️ Oh dear, error listing key bindings: {e}\033[0m")

def delete_keybinding(keybinding_id):
    try:
        result = subprocess.run(["dconf", "dump", "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/"], capture_output=True, text=True, check=True)
        keybindings = result.stdout.strip().splitlines()
        id = int(keybinding_id[2:])  # Remove the "KB" prefix
        if id > 0 and id <= len(keybindings) // 4:
            keybinding_name = keybindings[(id - 1) * 4]
            result = subprocess.run(["dconf", "write", f"/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/{keybinding_name}", "'[]'"], check=True)
            print(f"❤️ Keybinding '{keybinding_name}' deleted successfully, may it rest in peace ❤️")
        else:
            print("❗️ Oh dear, invalid keybinding ID.")
    except subprocess.CalledProcessError as e:
        print(f"\033[91m❗️ Oh dear, error deleting keybinding: {e}\033[0m")

def edit_keybindings():
    try:
        # Export keybindings to a temporary file
        with open("keybindings.tmp", "w") as f:
            subprocess.run(["dconf", "dump", "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/"], stdout=f, check=True)

        # Open the file in nano editor
        subprocess.run(["nano", "keybindings.tmp"], check=True)

        # Import the changes back into the dconf database
        with open("keybindings.tmp", "r") as f:
            subprocess.run(["dconf", "load", "/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/"], stdin=f, check=True)

        # Remove the temporary file
        os.remove("keybindings.tmp")

        print("✨❤️ Keybindings updated successfully, may your keyboard be forever happy ❤️✨")
    except subprocess.CalledProcessError as e:
        print(f"\033[91m❗️ Oh dear, error editing keybindings: {e}\033[0m")

def main():
    while True:
        print("\n✨ Ubuntu Keybindings Editor ✨")
        print("1. List keybindings 🔍")
        print("2. Delete keybinding ⚠️")
        print("3. Edit keybindings ✍️")
        print("4. Quit 👋")
        choice = input("Enter your choice: ")

        if choice == "1":
            list_keybindings()
        elif choice == "2":
            keybinding_id = input("Enter the ID of the keybinding to delete (e.g. KB1): ")
            delete_keybinding(keybinding_id)
        elif choice == "3":
            edit_keybindings()
        elif choice == "4":
            break
        else:
            print("❗️ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()