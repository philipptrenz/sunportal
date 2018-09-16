# sunportal

_sunportal_ is a web based visualisation tool to display data of SMA solar inverters. It is based on the database of [SBFspot](https://github.com/SBFspot/SBFspot) and shows charts of this and previous days on a website. It runs on a Raspberry Pi and can handle multiple inverters in one Speedwire or Bluetooth(R) network.

![sunportal example image](/html/img/sunportal.jpg?raw=true)

## Installation on a Raspberry Pi

First install and configure SBFspot as described [here](https://github.com/SBFspot/SBFspot/wiki/Installation-Linux-SQLite#sbfspot-with-sqlite), the _SBFspotUploadDaemon_ is not required. 

Also add a cronjob for SBFspot to run every 5 minutes. Execute `sudo crontab -e`, choose your preferred editor and add the following line:

```
*/5 * * * * /usr/local/bin/sbfspot.3/SBFspot -finq -nocsv > /dev/null
```

After that install _sunportal_:

**No installation instructions for python yet!**

## Disclaimer

SMA, Speedwire are registered trademarks of SMA Solar Technology AG.
