# SunPortal

![sunportal example image](http://cloud.philipptrenz.de/index.php/apps/gallery/s/DAppzj9DyHPBx8i)


## Installation

First install and configure SBFspot. After that install SunPortal:

```
# Install apache and php
sudo apt update && sudo apt upgrade
sudo apt install apache2 php php-sqlite3

# Copy the contents of the html directory to /var/www/html
sudo cp -r * /var/www/html

# Make a link to the SBFspot database 
sudo ln /home/pi/smadata/SBFspot.db /var/www/html/SBFspot.db

# Update permissions
sudo chown -R pi:www-data /home/pi/smadata/
sudo chown -R pi:www-data /var/www/html/
sudo chmod -R 770 /var/www/html/

# reboot
sudo reboot
```
