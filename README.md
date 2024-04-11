# rpi-accesspoint
Access point for a raspberry pi

## Setup
1. Install raspberry pi imager from: https://www.raspberrypi.com/software/
2. In advanced options, enable ssh and set authorized keys of your ssh public key (cat ~/.ssh/id_ed25519.pub) and locale options.
3. **BELOW PROBABLY NOT REQUIRED CURRENTLY:** For ssh access from OSX, mount the freshly minted SD card and:
   * `touch ssh` NB: not needed if ssh was enabled in step 2.
   * Edit `config.txt` and append `dtoverlay=dwc2`
   * Edit `cmdline.txt` and after `rootwait` append the text `modules-load=dwc2,g_ether`
4. Copy `roles/ap-client/files/wpa_supplicant.conf` into boot directory of flash card.
   On osx: `cp /opt/rpi-accesspoint/roles/ap-client/files/wpa_supplicant.conf /Volumes/boot/`
5. Put card in Rpi and boot

### Enable wifi
**NB:** Below may not be relevant if wpa_supplicant.conf copied into rpi boot directory.
Wi-Fi is blockeded by rfkill by default.
Can use raspi-config for setup i.e. the country, before use.

```sudo raspi-config nonint do_wifi_country GB```

### External wifi adapator
* https://www.tp-link.com/uk/home-networking/adapter/tl-wn725n/ - uses RTL8188EUS driver

### Login
To login: `ssh pi@raspberrypi.local`

#### Additional configuration to use vi as default editor
**NB: Below seems uneeded now.

Add to ```~/.profile```
```
set -o emacs
export EDITOR=/usr/bin/vi
```

Then keep for sudo access
```
sudo visudo
Defaults env_keep += "EDITOR"
```

### Install Ansible on Host machine to enable connection to Raspberry Pi
1. Create a virtual environment in the directory $HOME/.venv for installing ansible:  
  `python3 -m venv ~/.venv`
2. Activate python virtual environment on login: add following to ~/.profile:  
  `source $HOME/.venv/bin/activate`
3. Install ansible with pip:  
  `python3 -m pip install ansible`
4. For manipulating network addresses:  
  `python3 -m pip install netaddr`

### Run Ansible
1. Edit file `ap-client.yml` in main directory  to set any variables (e.g. tailscale).
2. Execute with:  
  `ansible-playbook -i inventory.yml  ap-client.yml `

### To Activate tailsale
1. Started by tailscale-start service.
2. Check status with:  
  `sudo systemctl status tailscale-start.service`
3. If started, enter:
   `tailscale status`
   This will provide a URL to log in, so paste this into a browser logged into the google account linked to tailscale.


### References:
* Offical guide to set up AP:  
   https://www.raspberrypi.com/documentation/computers/configuration.html#setting-up-a-routed-wireless-access-point
* Discussion on proper way to set up bridge:  
   https://raspberrypi.stackexchange.com/questions/89803/access-point-as-wifi-router-repeater-optional-with-bridge
* Good general discussion on networking on Rpi:  
  https://raspberrypi.stackexchange.com/questions/37920/how-do-i-set-up-networking-wifi-static-ip-address-on-raspbian-raspberry-pi-os/37921#37921
* primer on debugging network issues:  
   https://www.redhat.com/sysadmin/beginners-guide-network-troubleshooting-linux
* Ansible project to create an rpi AP:  
  https://github.com/jsphpl/ansible-raspi-accesspoint
* See also RaspAP project:  
  https://github.com/RaspAP/raspap-tools
* Great project to configure an RPI:  
  https://github.com/glennklockwood/rpi-ansible


  ### Install driver for TP-Link ARcher T2U Plus
  https://github.com/aircrack-ng/rtl8812au

```
sudo apt-get install raspberrypi-kernel-headers
git clone -b v5.6.4.2 https://github.com/aircrack-ng/rtl8812au.git
cd rtl*

sed -i 's/CONFIG_PLATFORM_I386_PC = y/CONFIG_PLATFORM_I386_PC = n/g' Makefile
sed -i 's/CONFIG_PLATFORM_ARM64_RPI = n/CONFIG_PLATFORM_ARM64_RPI = y/g' Makefile

export ARCH=arm
sed -i 's/^MAKE="/MAKE="ARCH=arm\ /' dkms.conf

make
sudo make -n install
```

Generated command:

```
install -p -m 644 88XXau.ko  /lib/modules/5.15.76-v7l+/kernel/drivers/net/wireless/
# /sbin/depmod -a 5.15.76-v7l+
``` 

### Change MAC Address
Had to change the Mac Address of lettusgrow raspberry pi:
# Change Mac Address of wlan0

`/etc/systemd/network/00-default.link`

```
[Match]
MACAddress=b8:27:eb:bb:5d:9b

[Link]
MACAddress=02:68:b3:29:da:98
NamePolicy=kernel database onboard slot path
```

