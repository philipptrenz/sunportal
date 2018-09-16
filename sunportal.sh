#!/bin/sh
#
# init script for sunportal
#

### BEGIN INIT INFO
# Provides:          sunportal
# Required-Start:    $remote_fs $syslog $network
# Required-Stop:     $remote_fs $syslog $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: init script for sunportal
# Description:       sunportal provides solar inverter data visualisation
### END INIT INFO

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
NAME=sunportal
DIR=/home/pi/sunportal
DAEMON=$DIR/sunportal.py
DAEMONARGS=""
PIDFILE=/var/run/$NAME.pid
LOGFILE=/var/log/$NAME.log

. /lib/lsb/init-functions

test -f $DAEMON || exit 0

case "$1" in
    start)
        start-stop-daemon --start --background \
            --pidfile $PIDFILE --make-pidfile --chdir $DIR --startas /bin/bash \
            -- -c "exec stdbuf -oL -eL $DAEMON $DAEMONARGS > $LOGFILE 2>&1"
        log_end_msg $?
        ;;
    stop)
        start-stop-daemon --stop --pidfile $PIDFILE
        log_end_msg $?
        rm -f $PIDFILE
        ;;
    restart)
        $0 stop
        $0 start
        ;;
    status)
        start-stop-daemon --status --pidfile $PIDFILE
        log_end_msg $?
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 2
        ;;
esac

exit 0