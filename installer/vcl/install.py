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
    #download_modules(modules_dict)

    tar_file_path = get_file_name(modules_dict, "vcl")
    md5_file_path = get_file_name(modules_dict, "vcl-md5")

    md5_verified = verify_md5(tar_file_path, md5_file_path)
    if md5_verified == False:
        return

    #extract_modules(modules_dict)
    
    vcl_path = get_folder_path(modules_dict, "vcl")
    #install_vcl(vcl_path)
    # TODO: Retreive the public IP address of the current machine (VM or 
    #       otherwise)
    install_webserver("vcl","localhost","vcluser", "vcluserpassword", 
                        "192.168.187.145")

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

    #remove("secrets.php")
    #move(abs_path, "secrets.php")
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
    
    #remove("conf.php")
    #move(abs_path, "conf.php")    
    
    # TODO: Update the help and error email ids in conf.php

    call(["chown", "apache", "maintenance"])
    
    os.chdir(saved_path)

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
