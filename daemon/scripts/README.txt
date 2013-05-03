Parent Image
-----------------------------------------------
Startup script:
1. present at /root/startup.sh
2. Runs automatically on boot, added in /etc/rc.local

Manual steps
1. > /sbin/ifconfig: note your ip address
2. > vim /etc/vcl/vcld.conf : change the ip address which you could see in this file to your ip address.
3. > /etc/init.d/vcld restart
4. > vim /var/www/html/vcl/.ht-inc/conf.php : Change the lines where you see old ip address with yours.
5. > /sbin/service httpd restart : Restart Httpd service
6. > tail -f /var/log/vcld.log : Check if management node has checked in.
7. > Login through web interface and see if it is working.
8. > Start the parent daemon kept parent_daemon folder

login: root
password: password


Child Image
------------------------------------------------
Startup script:
1. present at /root/startup.sh
2. Runs automatically on boot, added in /etc/rc.local

Manual steps
1. > /sbin/ifconfig: note your ip address
2. > vim /root/vcl_sshd_config : Change the Listen address on last line to your ip address.
3. > ps -aux | grep sshd : kill the sshd process running above file.
4. > /usr/sbin/sshd -f /root/vcl_sshd_config : Execute to run this sshd
5. > cd /home/vcluser/child_daemon : Run the child daemon (run_child.sh)

login: root
password: password

login: vcluser
password: MicroCloud
