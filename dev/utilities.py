import os
import time
import platform
import socket
import re
import subprocess
import shlex

preset: dict[str, str] = None
image_path: str = None
volume: str = None
mount_point: str = None
boot_path: str = None
hostname: str = None
ssh = None
sftp = None
http = None
default_user: bool = False

host = platform.uname()
if "darwin" in host.system.lower():
    boot_path = "/Volumes/boot"
if "linux" in host.system.lower():
    login = os.getlogin()
    boot_path = f"/run/media/{login}/boot"


def _get_option(option: str, default = None):
    answer = input(option).strip()
    if answer == "":
        if default is not None:
            return default
        return _get_option(option)
    return answer


def _get_bool(question, default = None):
    if default is None:
        answer = input(f"{question}[y/n]: ").strip().lower()
        if answer == "y" or answer == "yes":
            return True
        if answer == "n" or answer == "no":
            return False
        
    elif default is True:
        answer = input(f"{question}[Y/n]: ").strip().lower()
        if answer == "y" or answer == "yes" or answer == "":
            return True
        if answer == "n" or answer == "no":
            return False

    elif default is False:
        answer = input(f"{question}[y/N]: ").strip().lower()
        if answer == "y" or answer == "yes":
            return True
        if answer == "n" or answer == "no" or answer == "":
            return False

    return _get_bool(question, default)


def _require_preset(force = False):
    if not force and preset is not None: return

    def _new_preset():
        global preset
        preset = {
            "HOSTNAME": _get_option("Hostname? (default = \"pi\") ", default = "pi"),
            "USERNAME": _get_option("Username? (default = \"frt\") ", default = "frt"),
            "PASSWORD": _get_option("Password? "),
            "WLAN_SSID": _get_option("WLAN SSID (name of your WIFI network)? "),
            "WLAN_PASSWORD": _get_option("WLAN password? "),
            "WLAN_COUNTRY": _get_option("WLAN country code? (default = \"HU\") ", default = "HU")
        }

        string =    " {\n"\
                    "        \"HOSTNAME\": \"%s\",\n"\
                    "        \"USERNAME\": \"%s\",\n"\
                    "        \"PASSWORD\": \"%s\",\n"\
                    "        \"WLAN_SSID\": \"%s\",\n"\
                    "        \"WLAN_PASSWORD\": \"%s\",\n"\
                    "        \"WLAN_COUNTRY\": \"%s\",\n"\
                    "    }" % (
                        preset["HOSTNAME"], 
                        preset["USERNAME"], 
                        preset["PASSWORD"], 
                        preset["WLAN_SSID"], 
                        preset["WLAN_PASSWORD"],
                        preset["WLAN_COUNTRY"]
                    )
        print("\nGreat, it looks like this.\n")
        print("   " + string + "\n")
        if _get_bool("Would you like to try again? ", default = False):
            print()
            _new_preset()

        if _get_bool("\nShould we save the preset into ./presets.py? ", default = True):
            name = _get_option("What should we name the preset? (default = \"default\") ", default = "default")
            with open("./presets.py", "w") as file:
                print(
                    ("presets = {\n"
                    "    \"%s\":" + string +
                    ",\n}\n") % name, file = file
                )

    def _choose_preset():
        from presets import presets
        if len(presets) == 0:
            raise RuntimeError()
        s = "s" if len(presets) > 1 else ""
        print(f"I have found {len(presets)} preset{s} in ./presets.py.\n")

        keys = [key for key in presets]
        for i, key in enumerate(keys):
            print(f"    {i}) {key}")

        i = int(_get_option("\nWhich one would you like to use? (default = 0) ", default = "0"))
        global preset
        preset = presets[keys[i]]
        string =    " {\n"\
                    "        \"HOSTNAME\": \"%s\",\n"\
                    "        \"USERNAME\": \"%s\",\n"\
                    "        \"PASSWORD\": \"%s\",\n"\
                    "        \"WLAN_SSID\": \"%s\",\n"\
                    "        \"WLAN_PASSWORD\": \"%s\",\n"\
                    "        \"WLAN_COUNTRY\": \"%s\",\n"\
                    "    }" % (
                        preset["HOSTNAME"], 
                        preset["USERNAME"], 
                        preset["PASSWORD"], 
                        preset["WLAN_SSID"], 
                        preset["WLAN_PASSWORD"],
                        preset["WLAN_COUNTRY"]
                    )
        print("\nGreat, it looks like this.\n")
        print("   " + string + "\n")
        if _get_bool("Would you like to choose another one? ", default = False):
            print()
            _choose_preset()

    try:
        _choose_preset()
    except ModuleNotFoundError:
        print(
            "It looks like you do not have ./presets.py set up yet. " 
            "We will create a new preset now.\n"
        )
        _new_preset()
    except ImportError:
        print(
            "It looks like there are no presets in ./presets.py configured. " 
            "We will create a new preset now.\n"
        )
        _new_preset()
    except RuntimeError:
        print(
            "It looks like there are no presets in ./presets.py configured. " 
            "We will create a new preset now.\n"
        )
        _new_preset()


def get_hostname(raw: str):
    if "darwin" in host.system.lower():
        return raw + ".local"
    if "linux" in host.system.lower():
        cmd = shlex.split(f"avahi-resolve-host-name -4 {raw}.local")
        proc = subprocess.Popen(cmd, stdout = subprocess.PIPE)
        out, _ = proc.communicate()
        return out.decode().split("\t")[1][:-1]


def _require_hostname(force = False):
    global hostname
    if not force and hostname is not None: return
    _require_preset()
    if default_user:
        hostname = get_hostname("raspberrypi")
    else:
        hostname = get_hostname(preset["HOSTNAME"])
    

def _require_image_path(force = False):
    global image_path
    if not force and image_path is not None: return

    if _get_bool("Do you have the Raspberry OS Lite 64-bit image locally? ", default = False):
        image_path = _get_option("/path/to/file.img: ")
        print()
    else:
        image_path = "./raspberryos.img"
        link = "https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2022-09-26/2022-09-22-raspios-bullseye-arm64-lite.img.xz"
        print("Downloading image...\n")
        os.system(f"wget -c {link} -O raspberryos.img.xz")
        print("Decompressing image...\n")
        os.system("unxz raspberryos.img.xz --threads=0")
        print()


def _require_volume(force = False):
    global volume
    if not force and volume is not None: return

    print("Please insert an SD card into your computer. If you are done, press enter.")
    input()

    if "darwin" in host.system.lower():
        os.system("diskutil list")
        print("I suppose you are on Mac OS. Above is the output of command \"diskutil list\".")
        volume = _get_option("Which disk is your SD card? (e.g. /dev/rdisk5, you might have to place the \"r\" in it) ")

    if "linux" in host.system.lower():
        print("Listing available disks... (might ask for your password)\n")
        os.system("sudo fdisk -l")
        print("\nI suppose you are on Linux. Above is the output of command \"fdisk -l\".")
        volume = _get_option("Which disk is your SD card? (e.g. /dev/sda) ")


def _require_mount_point(force = False):
    global mount_point
    if not force and mount_point is not None: return

    if "darwin" in host.system.lower():
        mount_point = "/Volumes/boot"
    if "linux" in host.system.lower():
        _require_volume()
        mount_point = volume


def _require_ssh(force = False):
    import paramiko
    global ssh
    if not force and ssh is not None: return
    _require_preset()
    _require_hostname()

    try:
        ssh = paramiko.client.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if default_user:
            ssh.connect(
                get_hostname("raspberrypi"), 
                username = "pi", 
                password = "raspberry",
                look_for_keys = False
            )
        else:
            ssh.connect(
                hostname, 
                username = preset["USERNAME"], 
                password = preset["PASSWORD"],
                look_for_keys = False
            )

    except socket.gaierror:
        print("Could not resolve hostname, retrying in 5 seconds...")
        time.sleep(5)
        ssh = None
        _require_ssh()
    except TimeoutError:
        print("Connection timeout, retrying in 5 second...")
        time.sleep(5)
        ssh = None
        _require_ssh()


def _require_sftp(force = False):
    import paramiko
    global sftp
    if not force and sftp is not None: return
    _require_preset()
    _require_hostname()

    class SFTPClient(paramiko.SFTPClient):
        def put_dir(self, source, target):
            ''' Uploads the contents of the source directory to the target path. The
                target directory needs to exists. All subdirectories in source are 
                created under target.
            '''
            for item in os.listdir(source):
                if os.path.isfile(os.path.join(source, item)):
                    self.put(os.path.join(source, item), '%s/%s' % (target, item))
                else:
                    self.mkdir('%s/%s' % (target, item), ignore_existing=True)
                    self.put_dir(os.path.join(source, item), '%s/%s' % (target, item))

        def mkdir(self, path, mode = 511, ignore_existing = False):
            ''' Augments mkdir by adding an option to not fail if the folder exists  '''
            try:
                super(SFTPClient, self).mkdir(path, mode)
            except IOError:
                if ignore_existing:
                    pass
                else:
                    raise
    
    if default_user:
        transport = paramiko.Transport((get_hostname("raspberrypi"), 22))
        transport.connect(username=preset["USERNAME"], password=preset["PASSWORD"])
        sftp = SFTPClient.from_transport(transport)
    else:
        transport = paramiko.Transport((hostname, 22))
        transport.connect(username=preset["USERNAME"], password=preset["PASSWORD"])
        sftp = SFTPClient.from_transport(transport)


def _require_http():
    global http
    if http is not None: return
    _require_preset()


def _run(command: str, write: str = None):
    _require_ssh()
    stdin, stdout, stderr = ssh.exec_command(command)
    if write is not None:
        stdin.write(write.encode())
    stdin.close()
    while line := stdout.readline(): print(line, end = "")
    while line := stderr.readline(): print(line, end = "")


def _run_sudo(command: str, write: str = None):
    _require_ssh()
    stdin, stdout, stderr = ssh.exec_command("sudo -S -p '' " + command)
    stdin.write(preset["PASSWORD"] + "\n")
    if write is not None:
        stdin.write(write.encode())
    stdin.close()
    while line := stdout.readline(): print(line, end = "")
    while line := stderr.readline(): print(line, end = "")


def help():
    print(
"""Usage: ./manage.py [options...] commands...

CLI utility to automate common tasks during development.

Options:
    -p, --preset <name>         Use this preset when needed and do not ask
    -i, --image-path <path>     Use this image path when needed and do not ask
    -v, --volume <path>         Use this volume when needed and do not ask
    -u, --use-default-user      SSH and SFTP with default user and default hostname

Commands:
    help                Displays this message
    bootstrap           Performs a clean installation interactively
    ssh                 Starts a remote shell session
    build               Builds the project on the host
    clone               Clones the built project to the board
    shutdown            Shuts down the system of the board
    reboot              Reboots the system of the board
    restart             Restarts the systemd daemon on the board
    update              Updates the packages on the board
    eject               Ejects the SD card from the host
    set-wlan            Configures WLAN on the SD card in the host 

    write-image         Writes a system image to the SD card in the host
    install-deps        Installs depencencies on the board
    install-dev-deps    Installs development dependencies on the host
    configure-image     Prepares a written image for a headless setup
    configure-ssh       Performs basic tasks on the first boot"""
    )


def eject():
    _require_mount_point()
    print(f"Trying to unmount \"{mount_point}\"... (might ask for your password)")
    os.system(f"sudo umount {mount_point}")


def write_image():
    _require_image_path()
    _require_volume()

    if not _get_bool(f"Are you sure you want to erase all data on {volume}? ", default = False):
        print()
        _require_volume(force = True)
        write_image()
        return

    eject()
    time.sleep(3)

    print(f"\nWriting image \"{image_path}\" to volume \"{volume}\"... (this will take a while)")
    ec = os.system(f"sudo dd if={image_path} of={volume} status=progress")
    if ec != 0:
        print(
            "Writing image failed. The volume might still be mounted, be in read-only mode or may not exist.\n"
            "Check it and press enter to try again."
        )
        input()
        _require_volume(force = True)
        write_image()
        return
    print()


def set_wlan():
    _require_preset()
    print("Configuring WLAN connection \"%s\"..." % preset["WLAN_SSID"])
    content =   "country=%s\n"\
                "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n"\
                "update_config=1\n"\
                "network={\n"\
                "    ssid=\"%s\"\n"\
                "    scan_ssid=1\n"\
                "    psk=\"%s\"\n"\
                "    key_mgmt=WPA-PSK\n"\
                "}\n" % (preset["WLAN_COUNTRY"], preset["WLAN_SSID"], preset["WLAN_PASSWORD"])
    filename = f"{boot_path}/wpa_supplicant.conf"
    try:
        with open(filename, "w") as file:
            print(content, file = file)
    except FileNotFoundError:
            print(f"File \"{filename}\" not found. Is the SD card mounted?")        


def update():
    _require_ssh()
    print("Updating repository...")
    _run_sudo("apt update")
    print("\nUpgrading packages...")
    _run_sudo("apt upgrade -y")


def install_deps():
    _require_ssh()
    print("Installing dependencies...")
    _run_sudo("apt install python3-pip -y")
    _run("pip install -r /build/requirements.txt")


def install_dev_deps():
    os.system("python3 -m pip install -r requirements.txt")


def build():
    pass


def clone():
    _require_ssh()
    _require_sftp()
    try:
        print("Cloning \"./build\" directory to remote \"/build\"...")
        sftp.put_dir("./build", "/build")
    except PermissionError:
        print("Permission error. This usually happens when there are \"__pycache__\" directories somewhere in \"./build.\"")
        exit(-1)


def shutdown():
    _require_ssh()
    print("Shutting down system...")
    _run_sudo("shutdown --poweroff now")
    

def reboot():
    _require_ssh()
    print("Rebooting system...")
    _run_sudo("systemctl reboot")


def restart():
    _require_ssh()
    print("Restarting daemon...")
    _run_sudo("systemctl restart frt")


def configure_image():
    _require_preset()

    set_wlan()

    user = "pi:$6$/4.VdYgDm7RJ0qM1$FwXCeQgDKkqrOU3RIRuDSKpauAbBvP11msq9X58c8Que2l1Dwq3vdJMgiZlQSbEXGaY5esVHGBNbCxKLVNqZW1"
    try:
        print("Creating default user...")
        with open(f"{boot_path}/userconf.txt", "w") as file:
            print(user, file = file)

        print("Enabling SSH...")
        open(f"{boot_path}/ssh", "w").close()
    except FileNotFoundError:
        print(f"{boot_path} cannot be opened. Is the SD card mounted?")     


def configure_ssh():
    global default_user
    default_user = True
    _require_ssh(force = True)

    update()

    print("\nAdding user \"%s\"..." % preset["USERNAME"])
    _run("true | sudo useradd -M -G pi,adm,dialout,cdrom,sudo,audio,video,plugdev,games,users,input,render,netdev,gpio,i2c,spi %s" % preset["USERNAME"])

    print("\nSetting password...")
    _run_sudo("chpasswd", ("%s:%s\n" % (preset["USERNAME"], preset["PASSWORD"])))

    print("\nCreating directory /build...")
    _run_sudo("mkdir /build")

    print("\nSetting permissions...")
    _run_sudo("chown -R %s /build" % preset["USERNAME"])
    _run_sudo("chmod -R 750 /build")

    _require_sftp(force = True)
    print()
    clone()

    print("\nCreating service symlink...")
    _run_sudo("ln -s /build/frt.service /etc/systemd/system/frt.service")

    print("\nEnabling service...")
    _run_sudo("systemctl daemon-reload")
    _run_sudo("systemctl enable frt")

    print("\nSetting hostname to \"%s\"..." % preset["HOSTNAME"])
    _run_sudo("hostnamectl set-hostname %s" % preset["HOSTNAME"])

    print("\nDisabling login on default account...")
    _run_sudo("usermod pi -s /sbin/nologin")

    default_user = False
    _require_ssh(force = True)

    install_deps()

    time.sleep(5)
    reboot()
    print("After boot the board will be ready to use. Use \"ssh %s@%s.local\" to log in." % (preset["USERNAME"], preset["HOSTNAME"]))

    ssh = None
    sftp = None


def bootstrap():
    write_image()
    time.sleep(3)

    configure_image()
    time.sleep(3)

    eject()
    print("\nPut the SD card into your Raspberry Pi and power it up.\n")
    time.sleep(10)

    configure_ssh()


def ssh_session():
    _require_preset()
    _require_ssh()
    _require_hostname()
    if default_user:
        os.system("ssh pi@%s" % get_hostname("raspberrypi"))
    else:
        os.system("ssh %s@%s" % (preset["USERNAME"], hostname))
