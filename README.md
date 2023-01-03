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
1. Install
```
sudo apt-get install apt-transport-https
curl -fsSL https://pkgs.tailscale.com/stable/raspbian/bullseye.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg > /dev/null
curl -fsSL https://pkgs.tailscale.com/stable/raspbian/bullseye.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list
sudo apt-get update
sudo apt-get install tailscale
```

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


## Replace udev with file that creates interface on startup
systemctl edit --force --full accesspoint@.service

[Unit]
Description=accesspoint with hostapd (interface-specific version)
Wants=wpa_supplicant@%i.service

[Service]
ExecStartPre=/sbin/iw dev %i interface add ap@%i type __ap
ExecStart=/usr/sbin/hostapd -i ap@%i /etc/hostapd/hostapd.conf
ExecStopPost=-/sbin/iw dev ap@%i del

[Install]
WantedBy=sys-subsystem-net-devices-%i.device




