#!/usr/bin/python

import os
from subprocess import call
from tempfile import mkstemp
import shutil
from os import close
import MySQLdb as db
import sys

from utilities import Utilities

class WebserverInstaller:
    IPTABLES_CONF_FILEPATH = "/etc/sysconfig/iptables"

    # TODO: Refactor... method too long
    @staticmethod        
    def install(vcl_db, vcl_host, vcl_username, vcl_password,
                    webserver_ip_address):    
        call(["yum", "install", "httpd", "mod_ssl", "php", "php-gd",
                "php-mysql", "php-xml", "php-xmlrpc", "php-ldap", "-y"])
        call(["/sbin/chkconfig", "--level", "345", "httpd", "on"])
        call(["/sbin/service", "httpd", "start"])
    
        # Install the front end
        saved_path = os.getcwd()
        shutil.copytree("apache-VCL-2.3.1/web/", "/var/www/html/vcl")
        os.chdir("/var/www/html/vcl/.ht-inc")
        shutil.copy("secrets-default.php", "secrets.php")
    
        # Update the default values
        file_handler, abs_path = mkstemp()    
        
        old_file = open("secrets.php")
        temp_file = open(abs_path, 'w')
    
        parameters = dict()
        parameters["$vclhost"] = "'%s'" % vcl_host
        parameters["$vcldb"] = "'%s'" % vcl_db
        parameters["$vclusername"] = "'%s'" % vcl_username
        parameters["$vclpassword"] = "'%s'" % vcl_password
        parameters["$cryptkey"] = "'%s'" % Utilities.generate_random_text()
        parameters["$pemkey"] = "'%s'" % Utilities.generate_random_text()
    
        for line in old_file:
            if "=" in line:
                key, value = line.split('=')
                newline = "%s = %s;%s" % (key.strip(),
                                            parameters[key.strip()],
                                            value.split(';')[1])
                temp_file.write(newline)
            else:
                temp_file.write(line)
        
        old_file.close()
        temp_file.close()
        close(file_handler)
    
        # Copy from the temp file to secrets.php (so as not to loose the 
        # file permissions on secrets.php
        secrets_file = open("secrets.php", 'w')
        temp_file = open(abs_path)
    
        for line in temp_file:
            secrets_file.write(line)
    
        secrets_file.close()
    
        call("./genkeys.sh")
        shutil.copy("conf-default.php", "conf.php")
        # Update the IP address in conf.php
        file_handler, abs_path = mkstemp()
    
        old_file = open("conf.php")
        temp_file = open(abs_path, 'w')
    
        for line in old_file:
            if "vcl.example.org" in line:            
                newline = line.replace("vcl.example.org", webserver_ip_address)
                temp_file.write(newline)
            elif "\".example.org\"" in line:
                newline = line.replace(".example.org", "")
                temp_file.write(newline)
            else:
                temp_file.write(line)
        
        old_file.close()
        temp_file.close()
        close(file_handler)
    
        # Copy from the temp file to secrets.php (so as not to loose the 
        # file permissions on secrets.php
        conf_file = open("conf.php", 'w')
        temp_file = open(abs_path)
    
        for line in temp_file:
            conf_file.write(line)
    
        conf_file.close()
        
        # TODO: Update the help and error email ids in conf.php
        call(["chown", "apache", "maintenance"])
       
        # TODO: Do not hard coded the user and module name
        WebserverInstaller.add_management_node(
                                    database_ip_address=webserver_ip_address,
                                    hostname=vcl_host,
                                    username="admin",
                                    pred_module_name="predictive_level_0")
    
        os.chdir(saved_path)
    
    # TODO: Refactor... method too long
    @staticmethod
    def add_management_node(database_ip_address, hostname, username,
                pred_module_name):
        stateid = None
        ownerid = None
        premoduleid = None
        
        try:
            conn = db.connect(db="vcl")
            cursor = conn.cursor(db.cursors.DictCursor)
            cursor.execute("SELECT id FROM state WHERE name='available'")
            row = cursor.fetchone()
            if row is not None:
                stateid = row['id']
    
            cursor.execute("SELECT id FROM user WHERE unityid='%s'" % username)
            row = cursor.fetchone()
            if row is not None:
                ownerid = row['id']
    
            cursor.execute("SELECT id FROM module WHERE " 
                            "name='%s'" % pred_module_name)
            row = cursor.fetchone()
            if row is not None:
                premoduleid = row['id']
    
            cursor.close()
            conn.close()
        except db.Error, error:        
            print "MySQL error %d: %s" % (error.args[0], error.args[1])
            sys.exit(1)
    
        if (stateid is None) or (ownerid is None):
            print "Cannot retrieve stateid or owner id from the vcl database"
            sys.exit(1)
    
        # TODO: Check if parameterized insert statements are possible
        parameters = dict()
        parameters["hostname"] = hostname
        # TODO: Remove hard coding, move values if applicable to the config file
        parameters["IPaddress"] = database_ip_address
        parameters["ownerid"] = ownerid 
        parameters["stateid"] = stateid
        parameters["checkininterval"] = 5  # 5 secs
        parameters["installpath"] = ""
        parameters["imagelibenable"] = 0 
        parameters["imagelibgroupid"] = None
        parameters["imagelibuser"] = None
        parameters["imagelibkey"] = None
        parameters["keys"] = "/etc/vcl/vcl.key"
        parameters["premoduleid"] = premoduleid 
        parameters["sshport"] = 22
        parameters["publicIPconfig"] = "dynamicDHCP"
        parameters["publicnetmask"] = None
        parameters["publicgateway"] = None
        parameters["publicdnsserver"] = None
        parameters["sysadminemail"] = None
        parameters["sharedmailbox"] = None
    
        # TODO: Include conditional strings, include when not None
        query = ("INSERT INTO managementnode " 
                    "(hostname, " 
                    "IPaddress, " 
                    "ownerid, " 
                    "stateid, "  
                    "checkininterval, "  
                    "installpath, " 
                    "imagelibenable, " 
                    "imagelibgroupid, " 
                    "imagelibuser, " 
                    "imagelibkey, " 
                    "`keys`, " 
                    "predictivemoduleid, " 
                    "sshport, " 
                    "publicIPconfiguration, " 
                    "publicSubnetMask, " 
                    "publicDefaultGateway, " 
                    "publicDNSserver, " 
                    "sysadminEmailAddress, " 
                    "sharedMailBox" 
                    ")"
                " VALUES ('%s', "  # hostname
                    "'%s', "  # IPaddress
                    "%d, "  # ownerid
                    "%d, "  # stateid
                    "%d, "  # checkininterval                       
                    "'%s', "  # installpath
                    "%d,"  # imagelibenable
                    # ("NULL,", "%d,")[parameters["imagelibgroupid"] is not 
                    #   None]
                    "NULL,"  # imagelibgroupid
                    "NULL,"  # imagelibuser
                    "NULL,"  # imagelibkey
                    "'%s', "  # keys        
                    "%d, "  # premoduleid
                    "%d, "  # sshport
                    "'%s',"  # publicIPconfig
                    "NULL,"  # publicnetmask
                    "NULL,"  # publicgateway
                    "NULL,"  # publicdnsserver
                    "NULL,"  # sysminemail
                    "NULL"  # sharedmailbox
                    ")" % 
                (parameters["hostname"],
                 parameters["IPaddress"],
                 parameters["ownerid"],
                 parameters["stateid"],
                 parameters["checkininterval"],
                 parameters["installpath"],
                 parameters["imagelibenable"],
                 # parameters["imagelibgroupid"],
                 # parameters["imagelibuser"], 
                 # parameters["imagelibkey"], 
                 parameters["keys"],
                 parameters["premoduleid"],
                 parameters["sshport"],
                 parameters["publicIPconfig"],
                 # parameters["publicnetmask"], 
                 # parameters["publicgateway"], 
                 # parameters["publicdnsserver"],
                 # parameters["sysadminemail"],
                 # parameters["sharedmailbox"]
                 ))
    
        # TODO: Add code to rollback the transaction in case there is a failure
        try:
            conn = db.connect(db="vcl")
            cursor = conn.cursor(db.cursors.DictCursor)
    
            # Insert into managementnode table
            cursor.execute(query)
    
            cursor.execute("SELECT LAST_INSERT_ID()")
            row = cursor.fetchone() 
            if row is None:
                print "Unable to insert management node in the table"
                cursor.close()
                conn.close()
                sys.exit(1)
    
            last_insert_id = row["LAST_INSERT_ID()"]
    
            cursor.execute("SELECT id FROM resourcetype "
                                        "WHERE name='managementnode'")
            row = cursor.fetchone()
            managementnode_typeid = row['id']
    
            # Insert into resource table
            resource_query = ("INSERT INTO resource " 
                                "(resourcetypeid, subid) " 
                                "VALUES (%d, %d)" % 
                                (managementnode_typeid, last_insert_id))
    
            cursor.execute(resource_query)
    
            conn.commit()
            
            cursor.execute("SELECT LAST_INSERT_ID()")
            row = cursor.fetchone()
            if row is None:
                print "Unable to update the resource table"
                cursor.close()
                conn.close()
                sys.exit()
    
            resource_id = row["LAST_INSERT_ID()"]
            conn.close()
        except db.Error, error:        
            print "MySQL error %d: %s" % (error.args[0], error.args[1])
            sys.exit(1)
            
        try:
            conn = db.connect(db="vcl")
            cursor = conn.cursor(db.cursors.DictCursor)
            resource_group_query = ("SELECT id FROM resourcegroup WHERE "
                                    "name='%s'" % "allManagementNodes")
            cursor.execute(resource_group_query)
            row = cursor.fetchone()
            if row is None:
                print """Unable to retrieve the resource group id of 
                        allManagementNodes group"""
                cursor.close()
                conn.close()
                sys.exit()
    
            resource_group_id = row["id"]
            cursor.execute("INSERT INTO resourcegroupmembers"
                            "(resourceid, resourcegroupid) "
                            "VALUES(%d,%d)" % 
                            (resource_id, resource_group_id))
    
            conn.commit()
    
            cursor.close()
            conn.close()
        except db.Error, error:
            print "MySQL error %d: %s" % (error.args[0], error.args[1])
            sys.exit(1)
         
    @staticmethod   
    def update_firewall_rules():
    
        # TODO: Is there a better way to install the iptables rules, rather 
        #       than appending them to the end of the file (for example, check 
        #       if the rule exists before adding
        conf_file = open(WebserverInstaller.IPTABLES_CONF_FILEPATH, 'a')
        conf_file.write("-A RH-Firewall-1-INPUT -m state --state NEW -p tcp \
                            --dport 80 -j ACCEPT")
        conf_file.write("-A RH-Firewall-1-INPUT -m state --state NEW -p tcp \
                            --dport 443 -j ACCEPT")
        
        conf_file.close()
        call(["service", "iptables", "restart"])

