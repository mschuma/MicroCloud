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
    ext = ".tar.gz"
    for (module_name, url) in modules_dict.iteritems():
	    # TODO: Can use key/value pair in the config file
        # TODO: Check if the file exists 
        filename = url.split('/')[-1]
        if filename.endswith(ext) == False:
            continue

        print "[%s] from %s ..." % (module_name, filename)
        tar = tarfile.open(filename)
        tar.extractall()
        tar.close()
        folder_name = filename.strip(".tar.gz")

    print "Completed extracting modules\n"

def get_folder_path(modules_dict, module_name):
    ext = ".tar.gz"
    filename = modules_dict[module_name].split('/')[-1]
    if filename.endswith(ext):
        return filename[:-len(ext)]

def get_file_name(modules_dict, module_name):
    filename = modules_dict[module_name].split('/')[-1]
    return filename

def install_modules(config_filepath):
    # TODO: Add unit tests
    modules_dict = read_file(config_filepath)
    #download_modules(modules_dict)

    tar_file_path = get_file_name(modules_dict, "vcl")
    md5_file_path = get_file_name(modules_dict, "vcl-md5")

    md5_verified = verify_md5(tar_file_path, md5_file_path)
    if md5_verified == False:
        return

    extract_modules(modules_dict)
    
    vcl_path = get_folder_path(modules_dict, "vcl")
    install_vcl(vcl_path)

def install_vcl(vcl_path):
    # Install mysql
    # TODO: Check if mysql is installed before installing
    call(["yum", "install", "mysql-server", "-y"])

    # TODO: Check if mysql is running before starting 
    call(["/sbin/chkconfig", "--level", "345", "mysqld", "on"])
    call(["/sbin/service", "mysqld", "start"])

    configure_mysql()

def configure_mysql():
    try:
        conn = db.connect()

        conn.close()
    except db.Error, e:
        print "MySQL error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)

def update_firewall_rules(webserver_ip_address, webserver_port, 
                            management_node_ip_address, management_node_port):
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
