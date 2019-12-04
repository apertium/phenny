#!/bin/bash
#
# bot initscript
#
# Last Updated: Oct 31, 2011
# Modified for Apertium on Dec 28, 2012
# If broken, yell at: conor_f
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
LOGFILE="/home/begiak/logs/begiak.log"
USER="begiak"

start_bot() {
    start-stop-daemon -S -c $USER -p /var/run/$BOT.pid -m -d `dirname $EXEC` -b --startas /bin/bash -- -c "exec $EXEC $ARGS > $LOGFILE 2>&1"
    SUCCESS=$?
    if [ $SUCCESS -gt 0 ]; then
        echo "ERROR: Couldn't start $BOT"
    fi
    return $SUCCESS
}

stop_bot() {
    start-stop-daemon -K -p /var/run/$BOT.pid
    SUCCESS=$?
    if [ $SUCCESS -gt 0 ]; then
        echo "ERROR: Couldn't stop $BOT"
    fi
    return $SUCCESS
}

case "$1" in
    start)
        echo "Starting $BOT"
        start_bot
        ;;
    stop)
        echo "Stopping $BOT"
        stop_bot
        ;;
    restart)
        echo "Restarting $BOT"
        stop_bot
        if [ $? -gt 0 ]; then
            exit -1
        fi
        start_bot
        ;;
    force-reload)
        echo "Restarting $BOT"
        stop_bot
        if [ $? -gt 0 ]; then
            exit -1
        fi
        start_bot
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
