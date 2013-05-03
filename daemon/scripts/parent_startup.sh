#!/bin/sh

IP_ADDRESS=`ifconfig  | grep 'inet addr:'| grep -v '127.0.0.1' | cut -d: -f2 | awk '{ print $1}'`
PARENT_DAEMON_PATH="/root/parent_daemon"
PARENT_DAEMON_SCRIPT_NAME="run_parent.sh"

# Update the xml rpc uri IP address in vcld.conf
sed -i -e "s/xmlrpc_url=.*$/xmlrpc_url=https://$IP_ADDRESS/vcl/index.php?mode=xmlrpccall/g" /etc/vcl/vcld.conf 

# Update the IP address in httpd conf.php
sed -i -e "s/\$IP_ADDRESS=.*$/\$IP_ADDRESS=\"$IP_ADDRESS\";/g" /var/www/html/vcl/.ht-inc/conf.php

#Restart the services
/etc/init.d/vcld restart
/sbin/service httpd restart

PATH=$PATH:/usr/bin:$PARENT_DAEMON_PATH
echo "Running parent daemon at" $IP_ADDRESS
cd $PARENT_DAEMON_PATH
$PARENT_DAEMON_SCRIPT_NAME &

