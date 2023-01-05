# rpi-accesspoint
Access point for a raspberry pi

## Setup
1. Install raspberry pi imager from: https://www.raspberrypi.com/software/
2. In advanced options, enable ssh and set authorized keys of your ssh public key (cat ~/.ssh/id_ed25519.pub)
3. For ssh access from OSX, mount the freshly minted SD card and:
   * `touch ssh` NB: not needed if ssh was enabled in step 2.
   * Edit `config.txt` and append `dtoverlay=dwc2`
   * Edit `cmdline.txt` and after `rootwait` append the text `modules-load=dwc2,g_ether`
4. Check ssh access with: `ssh pi@raspberrypi.local`

Wi-Fi is blockeded by rfkill by default.
Can use raspi-config for setup i.e. the country, before use.
```sudo raspi-config nonint do_wifi_country GB```

It seems the easiest thing to get wlan0 set up is to use raspi-config to connect to an SSID.

#### Additional configuration to use vi as default editor
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

### Install Ansible
1. Create a virtual environment in the directory $HOME/.venv for installing ansible:
`python3 -m venv ~/.venv`
2. Activate python virtual environment on login: add following to ~/.profile:
`source $HOME/.venv/bin/activate`
3. Install ansible with pip:
`python3 -m pip install ansible`
4. For manipulating network addresses
`python3 -m pip install netaddr`

### Run Ansible
`ansible-playbook --syntax-check  -i inventory.yml  ap-client.yml `

### To Activate tailsale
1. Installs with playbook.
2. Login and use exit node
`sudo tailscale up --exit-node=100.95.9.30  --exit-node-allow-lan-access=true`


### References:
* Offical guide to set up AP
   https://www.raspberrypi.com/documentation/computers/configuration.html#setting-up-a-routed-wireless-access-point
* Discussion on proper way to set up bridge
   https://raspberrypi.stackexchange.com/questions/89803/access-point-as-wifi-router-repeater-optional-with-bridge
* Good general discussion on networking on Rpi:
  https://raspberrypi.stackexchange.com/questions/37920/how-do-i-set-up-networking-wifi-static-ip-address-on-raspbian-raspberry-pi-os/37921#37921
* primer on debugging network issues:
   https://www.redhat.com/sysadmin/beginners-guide-network-troubleshooting-linux
* Ansible project to create an rpi AP
  https://github.com/jsphpl/ansible-raspi-accesspoint


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

# install -p -m 644 88XXau.ko  /lib/modules/5.15.76-v7l+/kernel/drivers/net/wireless/
# /sbin/depmod -a 5.15.76-v7l+

