#!/usr/bin/python

from subprocess import call
import MySQLdb as db
import sys

    
class DatabaseInstaller:  
    IPTABLES_CONF_FILEPATH = "/etc/sysconfig/iptables"
    
    vcl_user_name = vcl_user_password = None
    webserver_ip_address = webserver_port = None
    management_node_ip_address = management_node_port = None
   
    # TODO: Encapsulate related arguments
    def __init__(self, user_name, password,
                        webserver_ip_address, webserver_port,
                        management_node_ip_address, management_node_port):
        self.vcl_user_name = user_name
        self.vcl_user_password = password
        
        self.webserver_ip_address = webserver_ip_address
        self.webserver_port = webserver_port
                
        self.management_node_ip_address = management_node_ip_address
        self.management_node_port = management_node_port        
    
    def install(self):
        # Install mysql
        # TODO: Check if mysql is installed before installing
        call(["yum", "install", "mysql-server", "-y"])
    
        # TODO: Check if mysql is running before starting 
        call(["/sbin/chkconfig", "--level", "345", "mysqld", "on"])
        call(["/sbin/service", "mysqld", "start"])
    
        self.configure()
    
    def configure(self):
        try:
            conn = db.connect()
            
            # Check whether vcl database exist
            conn.query("SHOW DATABASES WHERE `Database` = 'vcl'")
            results = conn.store_result()
    
            if results.num_rows() > 0:
                print "vcl database exists. Aborting..."
                conn.close()
                return
            
            # TODO: Do not hardcode localhost
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE vcl;\
                            GRANT SELECT,INSERT,UPDATE,DELETE,CREATE TEMPORARY \
                            TABLES ON vcl.* TO '%s'@'localhost' IDENTIFIED \
                            BY '%s'" % (self.vcl_user_name,
                                        self.vcl_user_password))
            cursor.close()
            conn.close()
        except db.Error, error:
            print "MySQL error %d: %s" % (error.args[0], error.args[1])
            sys.exit(1)
    
        # Import the sql dump
        call(["mysql", "vcl"], stdin=open("apache-VCL-2.3.1/mysql/vcl.sql"))
        
    def update_firewall_rules(self):
        # TODO: Is there a better way to install the iptables rules, rather 
        #       than appending them to the end of the file (for example, check 
        #       if the rule exists before adding
        conf_file = open(self.IPTABLES_CONF_FILEPATH, 'a')
        conf_file.write("-A RH-Firewall-1-INPUT -m state --state NEW -s " + 
                            self.webserver_ip_address + " -p tcp --dport " + 
                            self.webserver_port + " -j ACCEPT")
        conf_file.write("-A RH-Firewall-1-INPUT -m state --state NEW -s " + 
                            self.management_node_ip_address + 
                            " -p tcp --dport " + 
                            self.management_node_port + 
                            " -j ACCEPT")
         
        conf_file.close()
        call(["service", "iptables", "restart"])
