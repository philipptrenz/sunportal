
# SunPortal

## Installation

First install and configure SBFspot.

Copy database_script.py to `/home/pi/sbfdata/database_script.py` and add it to cron with crontab -e. Run every 5 minutes.
OR
Set the database pointer to `./html/SBFspot.db`

Then:

```
# Install apache and php
sudo apt update && sudo apt upgrade
sudo apt install apache2 php php-sqlite3

# Copy the contents of the html directory to /var/www/html
sudo cp -r * /var/www/html

# Make a link to the SBFspot database 
sudo ln -s /home/pi/smadata/SBFspot.db /var/www/html/SBFspot.db

# Update permissions
sudo chown -R pi:www-data /var/www/html/
sudo chmod -R 770 /var/www/html/

# reboot
sudo reboot
```
