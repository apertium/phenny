#!/bin/bash
#
# bot initscript
#
# Last Updated: Oct 31, 2011
# Modified for Apertium on Dec 28, 2012 and Dec 3, 2019
# If broken, yell at: conor_f, scoopgracie
#

### BEGIN INIT INFO
# Provides:		begiak
# Required-Start:	$network
# Required-Stop:	$network
# Default-Start:	3 4 5
# Default-Stop:		0 1 6
# Short-Description:	Begiak, Apertium's IRC bot
### END INIT INFO

BOT="begiak"
EXEC="/home/begiak/phenny/phenny"
ARGS="--config=/home/begiak/.phenny/default.py -v"
LOGFILE="/home/begiak/begiak.log"
USER="begiak"

start_bot() {
    start-stop-daemon -S -c $USER -p /var/run/$BOT.pid -m -d `dirname $EXEC` -b --startas /bin/bash -- -c "exec $EXEC $ARGS > $LOGFILE 2>&1"
    SUCCESS=$?
    if [ "$SUCCESS" -gt 0 ]; then
        echo "ERROR: Couldn't start $BOT"
    fi
    return $SUCCESS
}

stop_bot() {
    start-stop-daemon -K -p /var/run/$BOT.pid
    if [ "$?" -gt 0 ]; then
        echo "WARNING: STOPPING BOT FAILED"
    fi
    times=0
    while [ "$(ps -e | grep -c $(cat /var/run/$BOT.pid))" != 0 ]; do
        sleep 1
        times=$(($times+1))
        if [ ${times-0} -ge 60 ]; then
            kill -9 $(cat /var/run/$BOT.pid)
        fi
    done
    times=0
    while [ "$(ps -e | grep -c $(cat /var/run/$BOT.pid))" != 0 ]; do
        sleep 1
        times=$(($times+1))
        if [ ${times} -ge 15 ]; then
	    echo "ERROR: $BOT did not stop"
            SUCCESS=1
        fi
    done
    SUCCESS=$?
    if [ "$SUCCESS" -gt 0 ]; then
        echo "ERROR: Couldn't stop $BOT"
    fi
    return $SUCCESS
}

restart_bot() {
        stop_bot
        if [ "$?" -gt 0 ]; then
            echo "WARNING: bot may still be running; restarting anyway in 5 seconds, ^C to cancel"
	    sleep 5
        fi
        start_bot
        if [ "$?" -gt 0 ]; then
            exit 1
        fi
}

case "$1" in
    start)
        echo "Starting $BOT"
        start_bot
	exit $?
        ;;
    stop)
        echo "Stopping $BOT"
        stop_bot
	exit $?
        ;;
    restart)
        echo "Restarting $BOT"
        restart_bot
	exit $?
        ;;
    force-reload)
        echo "Restarting $BOT"
        restart_bot
	exit $?
        ;;
    status)
        if [ -e /var/run/$BOT.pid ]; then
            return 0
        fi
        return 3
        ;;
    *)
        echo "Usage: /etc/init.d/$BOT {start, stop, restart, force-reload, status}"
        exit 1
        ;;
esac

exit 0
