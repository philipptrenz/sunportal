1) Install and configure SBFspot
1a) Copy database_script.py to /home/pi/sbfdata/database_script.py and add it to cron with crontab -e. Run every 5 minutes.
OR
Set the database pointer to ./html/SBFspot.db
2) Install apache and php
3) Clone the html directory to /var/www/
4) Make a link to the SBFspot database in /home/pi/sbfdata/SBFspot.db from /var/www/html/SBFspot.db using: 

> ln /home/pi/sbfdata/SBFspot.db /var/www/html/SBFspot.db

4a) [EDIT] Permission changes must happen in order for the SBFspot database to be used.

5) Install unclutter (sudo apt-get install unclutter)
6) Edit the autostart file in the pi home directory (/home/pi) using: vim .config/lxsession/LXDE-pi/autostart

The following lines must be changed:

# CHANGED
#@xscreensaver -no-splash

The following lines must be added:

# Normal website that does not need any exceptions
@/usr/bin/chromium-browser --incognito --start-maximized --kiosk localhost
# Enable mixed http/https content, remember if invalid certs were allowed (ie self signed certs)
#@/usr/bin/chromium-browser --incognito --start-maximized --kiosk --allow-running-insecure-content --remember-cert-error-decisions localhost
@unclutter -idle 0
@xset s off
@xset s noblank
@xset -dpms
 
# END ADDED

7) Reboot and profit


##########################
## ENCOUNTERED PROBLEMS ##
##########################

*) Raspberry not using the entire screen:

Edit /boot/config.txt and uncomment the line:

disable_overscan=1