# sunportal

_sunportal_ is a web based visualisation tool to display data of SMA solar inverters. It is based on the database of [SBFspot](https://github.com/SBFspot/SBFspot) and shows charts of this and previous days on a website. It runs on a Raspberry Pi and can handle multiple inverters in one Speedwire or Bluetooth(R) network.

Current features:

* Web based visualization of daily and monthly power production
* Mail notification service for inverter disorders and lack of production

Planned features:

* Grouped inverter visualisation
* Visualization of yearly power production
* Validation of `config.json` per [JSON Schema](https://json-schema.org/)
* Configuration of _sunportal_ via web interface
* REST-API, i.e. to integrate power plants into home automation applications

If you like my project and want to keep me motivated:

<a href='https://ko-fi.com/U7U6COXD' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://az743702.vo.msecnd.net/cdn/kofi2.png?v=0' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>

Also check out my [s0-bridge](https://github.com/philipptrenz/s0-bridge) project for adding power consumption and production data of non-smart inverters to a SBFspot database by using external power meters with S0 interface!

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
sudo pip install flask pytz

# clone this repo
git clone https://github.com/philipptrenz/sunportal
cd sunportal
```

## Configure _sunportal_

All configuration parameters of _sunportal_ get stored inside the `config.json` json file. To edit the preconfigured values copy the `config.default.json` and edit the `config.json`:

```bash
cp config.default.json config.json
nano config.json
```

Under `mail` you can enable the integrated mail notification service by adding an SMTP server.

```json
{
	"database": {
		"path": "/home/pi/smadata/SBFspot.db"
	},
	"co2_avoidance_factor": 0.7,       
	"mail": {
		"enabled": "false",
		"check_interval": 300,         
		"sender": "sunportal@example.com",
		"smtp_server": {
			"url": "smtp.example.com",
			"port": 587
		},
		"recipients": [
			"me@example.com"
		],
		"starttls": {
			"enabled": "false",
			"user": "",
			"password": ""
		}
	}
}
```

## Start _sunportal_

```bash
sudo python3 sunportal.py
```

Open a browser and navigate to the IP address of the Raspberry Pi to see the website.

### Run _sunportal_ on boot

```bash
# make the scripts executable
sudo chmod 755 sunportal.*

# add the bash script to the service folder
sudo cp sunportal.sh /etc/init.d/sunportal
sudo update-rc.d sunportal defaults

```

Now _sunportal_ can be controlled as a service (`sudo service sunportal status`) and it automatically starts on boot.

## Disclaimer

SMA, Speedwire are registered trademarks of SMA Solar Technology AG.
