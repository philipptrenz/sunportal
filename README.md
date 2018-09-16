# sunportal

_sunportal_ is a web based visualisation tool to display data of SMA solar inverters. It is based on the database of [SBFspot](https://github.com/SBFspot/SBFspot) and shows charts of this and previous days on a website. It runs on a Raspberry Pi and can handle multiple inverters in one Speedwire or Bluetooth(R) network.

![sunportal example image](/static/img/sunportal.jpg?raw=true)

## Installation on a Raspberry Pi

First install and configure SBFspot as described [here](https://github.com/SBFspot/SBFspot/wiki/Installation-Linux-SQLite#sbfspot-with-sqlite), the _SBFspotUploadDaemon_ is not required. 

Also add a cronjob for SBFspot to run every 5 minutes. Execute `sudo crontab -e`, choose your preferred editor and add the following line:

```
*/5 * * * * /usr/local/bin/sbfspot.3/SBFspot -finq -nocsv > /dev/null
```

After that install _sunportal_:

```bash
# install needed dependencies
sudo apt-get install git python3 python3-pip 
sudo pip install flask sqlite3

# clone this repo
git clone https://github.com/philipptrenz/sunportal
cd sunportal

# and start
sudo python3 sunportal.py
```

If you want to run sunportal as a service on boot:
```bash
# make the scripts executable
sudo chmod 755 sunportal.py
sudo chmod 755 sunportal.sh

# add the bash script to the service folder
sudo cp sunportal.sh /etc/init.d
sudo update-rc.d sunportal.sh defaults

```
Now you can start and stop your script via `sudo service 433PyApi start` or `stop` and it automatically starts on boot.

## Disclaimer

SMA, Speedwire are registered trademarks of SMA Solar Technology AG.
