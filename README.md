# harmony-polyglot

This is the Harmony Hub Poly for the [Universal Devices ISY994i](https://www.universal-devices.com/residential/ISY) [Polyglot interface](http://www.universal-devices.com/developers/polyglot/docs/).  
(c) JimBoCA aka Jim Searle
MIT license. 


This node server is intended to support the [Logitech Harmony Hub](http://www.logitech.com/en-us/product/harmony-hub) using the [pyharmony Python Library](https://pypi.python.org/pypi/pyharmony).

*IMPORTANT:*  We have had reports that pulling in this node servers profile may mess up other node servers, like isylink.  Until this issue is resolved you may want to wait if that is an issue for you.

# Requirements

1. Currently you must be running at least the 0.0.4 release of Polyglot, put preferebly you should be on the latest release.
   http://ud-polyglot.readthedocs.io/en/development/usage.html#installation
2. This has only been tested on the ISY 5.0.4 Firmware, but should work with anything above 5.0.2
3. The required python modules are installed in Step 2 below.

# Install harmonyhub-polyglot

1. Backup Your ISY in case of problems!
  * Really, do the backup, please
2. Pull the harmonyhub-polyglot into Polyglot diretory on your RPi
  * `cd polyglot/config/node_servers`
  * `git clone https://github.com/jimboca/harmonyhub-polyglot.git`
  * `cd harmonyhub-polyglot`
  * `sudo pip install -r requirements.txt`
  * `sudo apt-get install zip unzip`
3. Create your config file
  * `cp config_template.yaml config.yaml`
  * `leafpad config.yaml`
  * Set the info about your Hub.
4. Build the config and profile
  * make config
  * make profile.zip
5. From the polyglot web page: http://your.pi.ip:8080
  * Refresh the page
  * Select 'Add Node Server'
  * Select 'Harmony Hub' as the 'Node Server Type'
  * Enter a name.
  * Enter a Node Server ID.  This MUST be the same 'Node Server' slot you intend to use from the ISY!!! So go look in the ISY NodeServer to see what slot is available.
  * Click Add, and it should show up on the left hand side and show 'Running', click on it.
  * Click on the 'Download profile' icon.
  * Select and Copy the 'Base URL' from that page, which you will need for Pasting later.
6. Add as NodeServer in ISY by selecting the empty slot that matches 'Node Server ID' you used in Step 4.
  * Set 'Profile Name' to whatever you want, but might as well be the same as the name used in Step 4.
  * Set the Polyglot 'User Id' and Password.  Default: admin & admin.
  * Paste the 'Base URL' you copied in Step 4.
  * Set Host Name or IP of your machine running Polyglot
  * Set Port to the Polyglot port, default=8080
7. Click 'Upload Profile'
  * Browse to where the 'harmonynub_profile.zip' from Step 4 is located and select it.
8. Reboot ISY by selecting the tab Configuration -> Reboot
9. Upload Profile again in the node server (quirk of ISY)
10. Reboot ISY again (quirk of ISY)
11. Once ISY is back up, go to Polyglot and restart the Harmony Hub server.
12. You should start to see your Harmony Hub and it's devices show up in the ISY
  * Select your Hub in the Left Pain
  * Right click on the Hub and select 'Group Devices'
13. Write programs and enjoy.

# Settings

## Server Node

The server node is the main node controlling the polyglot server.

* Status: Updated with the UNIX Epoch time.
* Version Major: The major version number of this program.
* Version Minor: The minor version number of this program.
* Hubs: The number of hubs the server is mananging
* Debug Mode: The Logging debug mode.
* Short Poll: The number of seconds between each time the Hub Nodes are polled to determine the current activity
* Long Poll: The number of seconds between each time the Hub Nodes send a DON which can be used to verify it is alive.

## Hub Node

The Hub node, one for each hub you define in the configuration.

## Activity Node

A Node for each activity in each hub.

## Device Node

A Node for each device defined in each hub.

# Debugging

This node server creates a log file as Polyglot/config/harmonyhub-polyglot/harmonyhub.log, where 'harmonyhub' is what you called the node server in Polyglot.  If you have any issues, first review that file, and also look for Errors with 'grep ERROR harmonyhub.log'.

The 'Debug level' of your HarmonyHub Servier in the ISY controls how much information shows up in this log.  To see more info set it to 'Debug'.  (Dont' use 'All', it is not currently working) 

# Programs

Monitoring can be done in the same way as detailed in the [Camera Server](https://github.com/jimboca/camera-polyglot#programs)

# Upgrading

1. On your machine running Polyglot
  * `cd polyglot/config/node_servers/harmonyhub-polyglot`
  * `rm -f profile/*/*`
  * `git pull`
  * `sudo pip install -r requirements.txt`
2. From any machine, open polyglot web page: http://your.pi.ip:8080
  * Select your harmonyhub on the left
  * Click the 'Restart Server' button nar the top right of the page.
3. If required for this release, you may also need to 'Update Profile' below.

# Update Profile

Whenever you edit the config file to add a Harmony Hub, or add activities or devices to your existing Harmony Hub(s) you will need to rebuild the config.
This must also be run sometimes when a new version of this program is released after running
the Upgrading steps above.

1. On your machine running Polyglot
  * `cd polyglot/config/node_servers/harmonyhub-polyglot`
  * make config
  * make profile.zip
2. From any machine, open polyglot web page: http://your.pi.ip:8080
  * Select your harmonyhub on the left
  * Click on the 'Download profile' icon near the top right
3. Open the ISY Admin Console
  * Select Menu: Node Servers -> Configure -> YourHarmonyServer
  * Click 'Upload Profile'
  * Browse to where the 'harmonynub_profile.zip' from Step 2 is located and select it.
  * Click OK in the Node Server Configuration
8. Reboot ISY by selecting the tab Configuration -> Reboot

# Release Notes

- 0.3.1:
   - Fix to call power_off so it only does set_activity(-1) if it's not powered off so devices don't toggle power.
- 0.3.0:
   - Add Change Channel to Hub which calls pyharmony change_channel
   - Must do the Upgrading and Update Profile steps!
- 0.2.0:
   - Fix to use label for send_command instead of name.
- 0.1.0:
   - First official release
- 0.0.2:
   - Never officially released, but was being used by some that like to live on the edge.
- 0.0.0:
   - This code is not officially released yet.  Consider it pre-alpha.

