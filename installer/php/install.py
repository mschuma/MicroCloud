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

def extract_modules(modules_dict):
    print "Extracting modules"
    for (module_name, url) in modules_dict.iteritems():
        # TODO: Can use key/value pair in the config file
        # TODO: Check if the file exists 
        filename = url.split('/')[-1]
        print "[%s] from %s ..." % (module_name, filename)
        tar = tarfile.open(filename)
        tar.extractall()
        tar.close()
        folder_name = filename.strip(".tar.gz")

    print "Completed extracting modules\n"

def install_modules(config_filepath, mysql_install_path, apache_install_path):
    # TODO: Move common methods to utility library
    # TODO: Add unit tests
    modules_dict = read_file(config_filepath)
    download_modules(modules_dict)
    extract_modules(modules_dict)

    php_path = get_folder_path(modules_dict, "php")
    install_php(php_path, mysql_install_path, apache_install_path)

def install_php(php_path, mysql_install_path, apache_install_path):
    print "Installing php"
    home = expanduser("~")
    # TODO: Remove hard coded path
    libpath = home+"/php"
    prefix = "--prefix="+libpath
    with_apxs2="--with-apxs2="+apache_install_path"/bin/apxs"
    with_mysql="--with-mysql="+mysql_install_path
    with_mysql_sock="--with-mysql-sock="+mysql_install_path+"/tmp/mysql.sock"
    arguments=[]
    arguments.append(prefix)
    arguments.append(with_apxs2)
    arguments.append(with_mysql)
    arguments.append(with_mysql_sock)
    configure_make_install(php_path, arguments)

home = expanduser("~")
mysql_install_path = home + "/mysql"
apache_install_path = home + "/apache"
install_modules("download_config", mysql_install_path, apache_install_path)
