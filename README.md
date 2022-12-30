# rpi-accesspoint
Access point for a raspberry pi

# Setup
1. Install raspberry pi imager from: https://www.raspberrypi.com/software/
2. In advanced options, enable ssh and set authorized keys of your ssh public key (cat ~/.ssh/id_ed25519.pub)
3. For ssh access from OSX, mount the freshly minted SD card and:
   * `touch ssh` NB: not needed if ssh was enabled in step 2.
   * Edit `config.txt` and append `dtoverlay=dwc2`
   * Edit `cmdline.txt` and after `rootwait` append the text `modules-load=dwc2,g_ether`

# Configure with Ansible
