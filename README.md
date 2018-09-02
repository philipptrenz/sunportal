# sunportal

sunportal is a web based visualisation tool to display data of a SMA solar inverter and is based on the database generated by [SBFspot](https://github.com/SBFspot/SBFspot). sunportal displays the daily and total yield as well as CO2 savings on a web page.

![sunportal example image](http://cloud.philipptrenz.de/index.php/apps/gallery/s/DAppzj9DyHPBx8i)

## Installation on a Raspberry Pi

First install and configure SBFspot. After that install SunPortal:

```
# Install apache and php
sudo apt update && sudo apt upgrade
sudo apt install apache2 php php-sqlite3 git

# Get repository
cd ~/ && git clone https://github.com/philipptrenz/SunPortal sunportal

# Copy the contents of the html directory to /var/www/html
sudo cp -r ~/sunportal/html/* /var/www/html

# Make a link to the SBFspot database 
sudo ln /home/pi/smadata/SBFspot.db /var/www/html/

# Set permissions
sudo chown -R pi:www-data /home/pi/smadata/
sudo chown -R pi:www-data /var/www/html/
sudo chmod -R 770 /var/www/html/

# reboot
sudo reboot
```
