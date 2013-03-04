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
    configure(php_path, apache_install_path)

def install_php(php_path, mysql_install_path, apache_install_path):
    print "Installing php"
    home = expanduser("~")
    # TODO: Remove hard coded path
    libpath = home+"/php"
    prefix = "--prefix="+libpath
    with_apxs2="--with-apxs2="+apache_install_path+"/bin/apxs"
    with_mysql="--with-mysql="+mysql_install_path
    with_mysql_sock="--with-mysql-sock="+mysql_install_path+"/tmp/mysql.sock"
    arguments=[]
    arguments.append(prefix)
    arguments.append(with_apxs2)
    arguments.append(with_mysql)
    arguments.append(with_mysql_sock)
    configure_make_install(php_path, arguments)

def configure_make_install(source_path, configure_arguments):
    saved_path = os.getcwd()
    os.chdir(source_path);

    configure_arguments.insert(0, "./configure")
    call(configure_arguments)
    call("make")
    call(["make", "install"])

    os.chdir(saved_path)

def get_folder_path(modules_dict, module_name):
    ext = ".tar.gz"
    filename = modules_dict[module_name].split('/')[-1]
    if filename.endswith(ext):
        return filename[:-len(ext)]

def configure(source_path, apache_install_path):
    home = expanduser("~")
    # TODO: Remove hard coded path
    install_path = home+"/php"

    saved_path = os.getcwd()
    os.chdir(source_path);

    # Copy php.ini-development to  $HOME/php/lib/php.ini
    template_ini_file = "php.ini-development"     
    shutil.copy(template_ini_file, install_path+"/lib/php.ini")
    
    os.chdir(saved_path)

    update_httpd_conf(apache_install_path)

def create_test_php(apache_install_path):
    f = open(apache_install_path + "/htdocs/test.php", "w")
    f.write("<?php phpinfo(); ?>")
    f.close()

def restart_apache(apache_install_path):
    apachectl_path = apache_install_path + "/bin/apachectl"
    call([apachectl_path, "-k", "restart"])

def update_httpd_conf(apache_install_path):
    f = open(apache_install_path + "/conf/httpd.conf", "a")
    f.write("AddHandler php5-script .php" + os.linesep)
    f.write("AddType text/html .php" + os.linesep)
    f.write("DirectoryIndex index.php" + os.linesep)
    f.close()

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
existing_files=os.listdir(os.getcwd())
mysql_install_path = home + "/mysql"
apache_install_path = home + "/apache"
install_modules("download_config", mysql_install_path, apache_install_path)
create_test_php(apache_install_path)
restart_apache(apache_install_path)
cleanup(existing_files)
