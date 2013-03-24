#!/usr/bin/python

import urllib
import threading
import tarfile
import os
from subprocess import call
from os.path import expanduser
from tempfile import mkstemp
from shutil import move
import shutil
from os import remove, close
import md5
import MySQLdb as db
import sys
import random
import string

def read_file(filepath):
    dictionary = dict()
    for line in open(filepath):
        key, value = line.split()
        dictionary[key.strip()] = value.strip() 
    
    return dictionary

def download_modules(modules_dict):
    print "Downloading modules"
    for (module_name, url) in modules_dict.iteritems():
        # TODO: Check for errors
        filename = url.split('/')[-1]
        # TODO: Include checksum in config file to verify
        # TODO: Pretty print in tabular format
        print "[%s] from %s ..." % (module_name, url)
        urllib.urlretrieve(url, filename)

    print "Completed downloading modules\n"

def verify_md5(tar_filepath, md5_filepath):
    md5_actual = md5.new(open(tar_filepath, "rb").read()).hexdigest()
    md5_expected = open(md5_filepath, "rb").read().split(' ')[0]
    print "Comparing MD5 hashes"
    if md5_actual == md5_expected:
        print "MD5 Checksum verified"
        return True

    print "MD5 Checksum does not match"
    return False
    
def extract_modules(modules_dict):
    print "Extracting modules"
    ext = ".tar.bz2"
    for (module_name, url) in modules_dict.iteritems():
	    # TODO: Can use key/value pair in the config file
        # TODO: Check if the file exists 
        filename = url.split('/')[-1]
        if filename.endswith(ext) == False:
            continue

        print "[%s] from %s ..." % (module_name, filename)
        tar = tarfile.open(filename, "r:bz2")
        for member in tar.getmembers():
            tar.extract(member, "")
        tar.close()
        folder_name = filename.strip(".tar.bz2")

    print "Completed extracting modules\n"

def get_folder_path(modules_dict, module_name):
    ext = ".tar.bz2"
    filename = modules_dict[module_name].split('/')[-1]
    if filename.endswith(ext):
        return filename[:-len(ext)]

def get_file_name(modules_dict, module_name):
    filename = modules_dict[module_name].split('/')[-1]
    return filename

def generate_random_text():
   random_chars = "".join([random.choice(string.letters) for i in xrange(30)])
   return random_chars

def install_modules(config_filepath):
    # TODO: Add unit tests
    modules_dict = read_file(config_filepath)
    download_modules(modules_dict)

    tar_file_path = get_file_name(modules_dict, "vcl")
    md5_file_path = get_file_name(modules_dict, "vcl-md5")

    md5_verified = verify_md5(tar_file_path, md5_file_path)
    if md5_verified == False:
        return

    extract_modules(modules_dict)
    
    vcl_path = get_folder_path(modules_dict, "vcl")
    install_vcl(vcl_path)
    # TODO: Retreive the public IP address of the current machine (VM or 
    #       otherwise)
    # TODO: Move value to configuration file or prompt user for input  
    parameters = dict()
    parameters["database_name"] = "vcl"
    parameters["database_user"] = "vcluser"
    parameters["database_password"] = "vcluserpassword"
    parameters["hostname"] = "localhost"
    parameters["server_ip_address"] = "192.168.187.145"
    parameters["xmlrpc_password"] = "password"
    parameters["xmlrpc_url"] = \
                        ("https://%s/vcl/index.php?mode=xmlrpccall" % 
                        parameters["server_ip_address"])

    install_webserver(parameters["database_name"], parameters["hostname"], 
                        parameters["database_user"],
                        parameters["database_password"], 
                        parameters["server_ip_address"])

    install_management_node_components(parameters["hostname"], 
                        parameters["server_ip_address"],
                        parameters["database_user"],
                        parameters["database_password"],
                        parameters["xmlrpc_password"],
                        parameters["xmlrpc_url"])

def install_webserver(vcl_db, vcl_host, vcl_username, vcl_password, 
                        webserver_ip_address):
    # TODO: Modules list can be moved to config file
    call(["yum", "install", "httpd", "mod_ssl", "php", "php-gd", "php-mysql", 
            "php-xml", "php-xmlrpc", "php-ldap", "-y"])
    call(["/sbin/chkconfig", "--level", "345", "httpd", "on"])
    call(["/sbin/service", "httpd", "start"])

    # Install the front end
    saved_path = os.getcwd()
    shutil.copytree("apache-VCL-2.3.1/web/", "/var/www/html/vcl")
    os.chdir("/var/www/html/vcl/.ht-inc")
    shutil.copy("secrets-default.php", "secrets.php")

    # Update the default values
    fh, abs_path = mkstemp()

    old_file = open("secrets.php", 'r')
    temp_file = open(abs_path, 'w')

    dictionary = dict()
    dictionary["$vclhost"] = "'%s'" % vcl_host
    dictionary["$vcldb"] = "'%s'" % vcl_db
    dictionary["$vclusername"] = "'%s'" % vcl_username
    dictionary["$vclpassword"] = "'%s'" % vcl_password
    dictionary["$cryptkey"] = "'%s'" % generate_random_text()
    dictionary["$pemkey"] = "'%s'" % generate_random_text()

    for line in old_file:
        if "=" in line:
            key, value = line.split('=')
            newline = "%s = %s;%s" % (key.strip(), 
                                        dictionary[key.strip()], 
                                        value.split(';')[1])
            temp_file.write(newline)
        else:
            temp_file.write(line)
    
    old_file.close()
    temp_file.close()
    close(fh)

    # Copy from the temp file to secrets.php (so as not to loose the 
    # file permissions on secrets.php
    secrets_file = open("secrets.php", 'w')
    temp_file = open(abs_path, 'r')

    for line in temp_file:
        secrets_file.write(line)

    secrets_file.close()

    call("./genkeys.sh")
    shutil.copy("conf-default.php", "conf.php")
    # Update the IP address in conf.php
    fh, abs_path = mkstemp()

    old_file = open("conf.php", 'r')
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
    close(fh)

    # Copy from the temp file to secrets.php (so as not to loose the 
    # file permissions on secrets.php
    conf_file = open("conf.php", 'w')
    temp_file = open(abs_path, 'r')

    for line in temp_file:
        conf_file.write(line)

    conf_file.close()
    
    # TODO: Update the help and error email ids in conf.php

    call(["chown", "apache", "maintenance"])
    
    add_management_node(webserver_ip_address, vclhost)

    os.chdir(saved_path)

def add_management_node(database_ip_address, hostname):
    stateid = None
    ownerid = None
    premoduleid = None
    try:
        conn = db.connect(db = "vcl")
        cursor = conn.cursor(db.cursors.DictCursor)
        cursor.execute("SELECT id FROM state WHERE name='available'")
        row = cursor.fetchone()
        if row is not None:
            stateid = row['id']

        # TODO: Do not hard code user's unity id
        cursor.execute("SELECT id FROM user WHERE unityid='admin'")
        row = cursor.fetchone()
        if row is not None:
            ownerid = row['id']

        # TODO: Do not hard code predictive module name
        cursor.execute("SELECT id FROM module WHERE name='predictive_level_0'")
        row = cursor.fetchone()
        if row is not None:
            premoduleid = row['id']

        cursor.close()
        conn.close()
    except db.Error, e:
        print "MySQL error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)

    if (stateid is None) or (ownerid is None):
        print "Cannot retrieve stateid or owner id from the vcl database"
        sys.exit(1)

    # TODO: Check if parameterized insert statements are possible
    parameters = dict()
    parameters["hostname"] = hostname
    # TODO: Retreive machine's private IP address
    parameters["IPaddress"] = database_ip_address
    parameters["ownerid"] = ownerid 
    parameters["stateid"] = stateid
    parameters["checkininterval"] = 5 # 5 secs
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
            " VALUES ('%s', "    # hostname
                "'%s', "        # IPaddress
                "%d, "          # ownerid
                "%d, "          # stateid
                "%d, "        # checkininterval                       
                "'%s', "          # installpath
                "%d,"          # imagelibenable
                #("NULL,", "%d,")[parameters["imagelibgroupid"] is not None]# imagelibgroupid
                "NULL,"
                "NULL,"          # imagelibuser
                "NULL,"          # imagelibkey
                "'%s', "          # keys        
                "%d, "          # premoduleid
                "%d, "        # sshport
                "'%s',"          # publicIPconfig
                "NULL,"          # publicnetmask
                "NULL,"          # publicgateway
                "NULL,"          # publicdnsserver
                "NULL,"          # sysminemail
                "NULL"            # sharedmailbox
                ")" %        
            (parameters["hostname"],
             parameters["IPaddress"], 
             parameters["ownerid"],
             parameters["stateid"], 
             parameters["checkininterval"],
             parameters["installpath"], 
             parameters["imagelibenable"], 
             #parameters["imagelibgroupid"],
             #parameters["imagelibuser"], 
             #parameters["imagelibkey"], 
             parameters["keys"], 
             parameters["premoduleid"], 
             parameters["sshport"], 
             parameters["publicIPconfig"], 
             #parameters["publicnetmask"], 
             #parameters["publicgateway"], 
             #parameters["publicdnsserver"],
             #parameters["sysadminemail"],
             #parameters["sharedmailbox"]
             ))

    print query

    try:
        conn = db.connect(db = "vcl")
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

        lastInsertId = row["LAST_INSERT_ID()"]

        cursor.execute("SELECT id FROM resourcetype "
                                    "WHERE name='managementnode'")
        row = cursor.fetchone()
        managementnode_typeid = row['id']

        # Insert into resource table
        resource_query = ("INSERT INTO resource " 
                            "(resourcetypeid, subid) " 
                            "VALUES (%d, %d)" %
                            (managementnode_typeid, lastInsertId))

        print resource_query
        cursor.execute(resource_query)

        conn.commit()
        
        cursor.execute("SELECT LAST_INSERT_ID()")
        row = cursor.fetchone()
        if row is None:
            print "Unable to update the resource table"
            cursor.close()
            conn.close()
            sys.exit()

        resourceId = row["LAST_INSERT_ID()"]
        resourceGroupQuery = ("SELECT id FROM resourcegroup WHERE "
                                "name='%s'" % "allManagementNodes")
        cursor.execute(resourceGroupQuery)
        row = cursor.fetchone()
        if row is None:
            print """Unable to retrieve the resource group id of 
                    allManagementNodes group"""
            cursor.close()
            conn.close()
            sys.exit()

        resourceGroupId = row["id"]
        cursor.execute("INSERT INTO resourcegroupmembers"
                        "(resourceid, resourcegroupid) "
                        "VALUES(%d,%d)" %
                        (resourceId, resourceGroupId))

        conn.commit()

        cursor.close()
        conn.close()
    except db.Error, e:
        print "MySQL error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)

def install_management_node_components(hostname, database_ip_address, 
                                    database_user, database_password,
                                    xmlrpc_password, xmlrpc_url):
    shutil.copytree("apache-VCL-2.3.1/managementnode/", "/usr/local/vcl")
    call(["perl", "/usr/local/vcl/bin/install_perl_libs.pl"])
    if not os.path.exists("/etc/vcl"):
        os.mkdir("/etc/vcl")
    shutil.copy("/usr/local/vcl/etc/vcl/vcld.conf", "/etc/vcl/vcld.conf")

    # Install and start the vcld service
    shutil.copy("/usr/local/vcl/bin/S99vcld.linux", "/etc/init.d/vcld")
    call(["/sbin/chkconfig", "--add", "vcld"])
    call(["/sbin/chkconfig", "--level", "345", "vcld", "on"])
    call(["/sbin/service", "vcld", "start"])


    update_ssh_conf()
    update_vcld_conf(hostname, database_ip_address, database_user, 
                        database_password, xmlrpc_password, xmlrpc_url)

    # Set the vclsystem account password for xmlrpc api
    call(["/usr/local/vcl/bin/vcld", "-setup"])
                       
def update_ssh_conf():
    conf_filepath = "/etc/ssh/ssh_config"
    
    # TODO: Check whether the entries exist before appending (for each host)
    file = open(conf_filepath, 'a')
    file.write("    UserKnownHostsFile /dev/null\n")
    file.write("    StrictHostKeyChecking no\n")
    file.close()

def update_vcld_conf(hostname, database_ip_address, database_user, 
                        database_password, xmlrpc_password, xmlrpc_url):
    
    parameters = dict()
    parameters["FQDN"] = hostname
    parameters["server"] = database_ip_address
    parameters["LockerWrtUser"] = database_user
    parameters["wrtPass"] = database_password
    parameters["xmlrpc_pass"] = xmlrpc_password
    parameters["xmlrpc_url"] = xmlrpc_url 

    conf_filepath = "/etc/vcl/vcld.conf"

    fh, abs_path = mkstemp()

    old_file = open(conf_filepath, 'r')
    temp_file = open(abs_path, 'w')

    for line in old_file:
        words = line.split('=')
        if len(words) <= 1:
            temp_file.write(line)
            continue
        
        key, value = line.split('=')
        if key.strip() not in parameters:
            temp_file.write(line)
            continue

        value = parameters[key.strip()]
        temp_file.write("%s=%s\n" % (key.strip(), value))
    
    old_file.close()
    temp_file.close()
    close(fh)

    # Copy from the temp file to secrets.php (so as not to loose the 
    # file permissions on secrets.php
    conf_file = open(conf_filepath, 'w')
    temp_file = open(abs_path, 'r')

    for line in temp_file:
        conf_file.write(line)

    conf_file.close() 

def install_vcl(vcl_path):
    # Install mysql
    # TODO: Check if mysql is installed before installing
    call(["yum", "install", "mysql-server", "-y"])

    # TODO: Check if mysql is running before starting 
    call(["/sbin/chkconfig", "--level", "345", "mysqld", "on"])
    call(["/sbin/service", "mysqld", "start"])

    configure_mysql("vcluser", "vcluserpassword")

def configure_mysql(vcl_username, vcl_password):
    try:
        conn = db.connect()
        
        # Check whether vcl database exist
        conn.query("SHOW DATABASES WHERE `Database` = 'vcl'")
        results = conn.store_result()

        if results.num_rows() > 0:
            print "vcl database exists. Aborting..."
            conn.close()
            return

        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE vcl;\
                        GRANT SELECT,INSERT,UPDATE,DELETE,CREATE TEMPORARY \
                        TABLES ON vcl.* TO '%s'@'localhost' IDENTIFIED \
                        BY '%s'" % (vcl_username, vcl_password))
        cursor.close()
        conn.close()
    except db.Error, e:
        print "MySQL error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)

    # Import the sql dump
    call(["mysql", "vcl"], stdin=open("apache-VCL-2.3.1/mysql/vcl.sql"))

def update_webserver_firewall_rules():

    conf_filepath = "/etc/sysconfig/iptables"

    # TODO: Is there a better way to install the iptables rules, rather than
    #       appending them to the end of the file (for example, check if the 
    #       rule exists before adding
    conf_file = open(conf_filepath, 'a')
    conf_file.write("-A RH-Firewall-1-INPUT -m state --state NEW -p tcp \
                        --dport 80 -j ACCEPT")
    conf_file.write("-A RH-Firewall-1-INPUT -m state --state NEW -p tcp \
                        --dport 443 -j ACCEPT")
    
    conf_file.close()
    call(["service", "iptables", "restart"])


def update_mysql_firewall_rules(webserver_ip_address, 
                                webserver_port, 
                                management_node_ip_address, 
                                management_node_port):
    conf_filepath = "/etc/sysconfig/iptables"

    # TODO: Is there a better way to install the iptables rules, rather than
    #       appending them to the end of the file (for example, check if the 
    #       rule exists before adding
    conf_file = open(conf_filepath, 'a')
    conf_file.write("-A RH-Firewall-1-INPUT -m state --state NEW -s " + 
                        websever_ip_address + " -p tcp --dport " + 
                        webserver_port + " -j ACCEPT")
    conf_file.write("-A RH-Firewall-1-INPUT -m state --state NEW -s " + 
                        management_node_ip_address +
                        " -p tcp --dport " +
                        management_node_port +
                        " -j ACCEPT")
     
    conf_file.close()
    call(["service", "iptables", "restart"])

def cleanup(existing_files):
    folder=os.getcwd()
    for entry in os.listdir(folder):
        if entry in existing_files:
            continue            
        path = os.path.join(folder,entry)        
        if os.path.isfile(path):
            os.unlink(path)
            print "Deleted "+path
        elif os.path.isdir(path):
            print "Deleted "+path
            shutil.rmtree(path)

home = expanduser("~")
#existing_files=os.listdir(os.getcwd())
install_modules("download_config")
#cleanup(existing_files)
