# harmony-polyglot

This is the Harmony Hub Poly for the [Universal Devices ISY994i](https://www.universal-devices.com/residential/ISY) [Polyglot interface](http://www.universal-devices.com/developers/polyglot/docs/).  
(c) JimBoCA aka Jim Searle
MIT license. 


This node server is intended to support the [Logitech Harmony Hub](http://www.logitech.com/en-us/product/harmony-hub) using the [pyharmony Python Library](https://pypi.python.org/pypi/pyharmony).

*IMPORTANT:*  We have had reports that pulling in this node servers profile may mess up other node servers, like isylink.  Until this issue is resolved you may want to wait if that is an issue for you.

# Requirements

1. Currently you must be running at least the 0.0.4 release of Polyglot
   http://forum.universal-devices.com/topic/19091-polyglot-version-004-release
2. This has only been tested on the ISY 5.0.4 Firmware, but should work with anything above 5.0.2
3. Install required python modules as instructed in Install Step #1

# Install

1. Backup Your ISY in case of problems!
  * Really, do the backup, please
2. Pull the harmonyhub-polyglot into Polyglot
  * `cd polyglot/config/node_servers`
  * `git clone https://github.com/jimboca/harmonyhub-polyglot.git`
  * `cd harmonyhub-polyglot`
  * `sudo pip install -r requirements.txt`
3. Create your config file
  * cp config_template.yaml config.yaml
  * leafpad config.yaml
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
8. Reboot ISY
9. Upload Profile again in the node server (quirk of ISY)
10. Reboot ISY again (quirk of ISY)
11. Once ISY is back up, go to Polyglot and restart the Harmony Hub server.
12. You should start to see your Harmony Hub and it's devices show up in the ISY
  * Select the Hub
  * Right click on the Hub and select 'Group Devices'
13. Write programs and enjoy.

# Settings

## Server Node

The server node is the main node controlling the polyglot server.

* Status: Is updated with the UNIX Epoch time.
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

# Programs

THIS NEEDS TO BE UPDATE For the Harmony Hub Server, but the general idea is the same.

Create programs on the ISY to monitor the Camera Server.

1. First create a state variable s.Polyglot.HubServer, or whatever you want to call it.
2. Create all the following programs

   * I put them all in a subfolder:
<pre>
    ===========================================
    Polyglot - [ID 025B][Parent 0001]

    Folder Conditions for 'Polyglot'

    If
       - No Conditions - (To add one, press 'Schedule' or 'Condition')
 
    Then
       Allow the programs in this folder to run.
</pre>

   * Heartbeat Monitor
<pre>
    -------------------------------------------
    CamS - [ID 025C][Parent 025B]

    If
        'Camera Server' is switched On
 
    Then
        $s.Polyglot.HubServer  = 1
        Wait  5 minutes 
        $s.Polyglot.HubServer  = 2
 
    Else
        $s.Polyglot.HubServer  = 2
 
    Watch for CamS DON, wait 5 minutes and set error if not seen.
</pre>

  * Okay notification
<pre>
    -------------------------------------------
    CamS Okay - [ID 0260][Parent 025B]

    If
        $s.Polyglot.HubServer is 1
 
    Then
        Send Notification to 'Pushover-P1' content 'Polyglot Status'
 
    This will be sent when CamS status is changed from anything to 1.
    Which means it will be sent when a problem is fixed, or ISY is starting up.
</pre>

   * Problem Notification
<pre>
    -------------------------------------------
    CamS Problem - [ID 025D][Parent 025B]

    If
        $s.Polyglot.HubServer is 2
 
    Then
        Send Notification to 'Pushover-P1' content 'Polyglot Status'
 
    CamS status 2 is a problem, send notification.
</pre>

   * Daily Problem reminder
<pre>
    -------------------------------------------
    CamS Problem Reminder - [ID 025F][Parent 025B]

    If
        $s.Polyglot.HubServer is 2
    And (
             Time is  8:00:00AM
          Or Time is  6:00:00PM
        )
 
    Then
        Send Notification to 'Pushover-P1' content 'Polyglot Status'
 
    CamS status 2 is a problem, send notification every day.
</pre>

   * Startup action
<pre>
    -------------------------------------------
    CamS Startup - [ID 025E][Parent 025B]

    If
        $s.Polyglot.HubServer is 0
 
    Then
        Run Program 'CamS' (Then Path)
 
    CamS init is zero, which only happens at startup, so start watching the CamS.
</pre>

3. Create a custom notification 'Polyglot Status':
<pre>
Subject: ISY: Polyglot Status
Body:
CameraServer Status: ${var.2.155}
0: Not initialized
1: Okay
2: Not responding

</pre>

# Release Notes:

- 0.0.0:
   - This code is not officially released yet.  Consider it pre-alpha.

