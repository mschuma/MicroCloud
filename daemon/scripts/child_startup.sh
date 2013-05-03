#!/bin/sh

IP_ADDRESS=`ifconfig  | grep 'inet addr:'| grep -v '127.0.0.1' | cut -d: -f2 | awk '{ print $1}'`
VCL_SSHD_CONFIG_PATH="/root/vcl_sshd_config"
CHILD_DAEMON_PATH="/home/vcluser/child_daemon"
CHILD_DAEMON_SCRIPT_NAME="run_child.sh"
CONTAINS_IP=`cat $VCL_SSHD_CONFIG_PATH | grep ListenAddress`

if [[ $CONTAINS_IP = "" ]]; then
	echo "Adding sshd listen address..." $IP_ADDRESS
	echo -n ListenAddress $IP_ADDRESS >> $VCL_SSHD_CONFIG_PATH
fi

/usr/sbin/sshd -f $VCL_SSHD_CONFIG_PATH

PATH=$PATH:/usr/bin:$CHILD_DAEMON_PATH
echo "Running child daemon with listen address" $IP_ADDRESS
cd $CHILD_DAEMON_PATH
$CHILD_DAEMON_SCRIPT_NAME &

