'''

        subprocess.run(
            f"dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/binding "'<Primary><Super><Alt>space'" && dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/command '/usr/bin/notify-send 111; {script_path}'",
            shell=True
        )
        subprocess.run(
            f"dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom1/binding "'<Primary><Super><Alt>p'" && dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom1/command '/usr/bin/notify-send DeactivatePanikMode; rm /tmp/panik_mode && {script_path}'",
            shell=True
        )
        subprocess.run(
            f"dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom2/binding "'<Primary><Super><Alt>o'" && dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom2/command '/usr/bin/notify-send ActivatePanikMode; {script_path}'",
            shell=True
        )
'''