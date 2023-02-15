#!/usr/bin/env python3

import dev.utilities as util
import sys

functions = {
    "help": util.help,
    "eject": util.eject,
    "write-image": util.write_image,
    "set-wlan": util.set_wlan,
    "update": util.update,
    "install-deps": util.install_deps,
    "install-dev-deps": util.install_dev_deps,
    "build": util.build,
    "clone": util.clone,
    "shutdown": util.shutdown,
    "reboot": util.reboot,
    "restart": util.restart,
    "configure-image": util.configure_image,
    "configure-ssh": util.configure_ssh,
    "bootstrap": util.bootstrap,
    "ssh": util.ssh_session
}

commands = []

try:
    i = 0
    while i < len(sys.argv):
        i += 1
        arg = sys.argv[i]
        if arg[0] == "-" and arg[1] == "-":
            option = arg[2:]
        elif arg[0] == "-": 
            option = arg[1]
        else:
            break

        if option == "p" or option == "preset":
            i += 1
            try:
                from presets import presets
                util.preset = presets[sys.argv[i]]
            except:
                print("Could not find such preset in ./presets.py.")

        elif option == "v" or option == "volume":
            i += 1
            util.volume = sys.argv[i]

        elif option == "i" or option == "image-path":
            i += 1
            util.image_path = sys.argv[i]

        elif option == "u" or option == "use-default-user":
            util.default_user = True

        else: raise

    while i < len(sys.argv):
        commands.append(sys.argv[i])
        i += 1

except:
    util.help()
    exit()

for command in commands:
    try:
        f = functions[command]
    except:
        util.help()
        exit()
    f()

    
