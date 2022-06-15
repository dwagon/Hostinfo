#!/bin/bash -x
if [ ${LOGNAME} != "hostinfo" ];then
    sudo su - hostinfo -c "/opt/hostinfo/Hostinfo/hostinfo/start.sh" -s /bin/bash
    exit $?
fi

export APPHOME="/opt/hostinfo/Hostinfo/hostinfo"
export GUNICORN="/opt/hostinfo/bin/gunicorn"
export NAME="hostinfo"
export USER="${NAME}"
export GROUP="${NAME}"

export PIDFILE="/var/run/$NAME.pid"
export LOGFILE="/var/log/$NAME.log"
export LOGLEVEL="info"
export DEBUG=True
export PORT=8000
export WORKERS=2

source /opt/hostinfo/bin/activate

$GUNICORN --pid="$PIDFILE" --name="$NAME" --workers=$WORKERS --user="$USER" --group="$GROUP" --log-file="$LOGFILE" --log-level="$LOGLEVEL" --bind="127.0.0.1:$PORT" --chdir $APPHOME --preload  ${NAME}.wsgi
exit $?

# EOF
