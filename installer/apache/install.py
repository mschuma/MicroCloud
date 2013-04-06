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

def install_apr(apr_path):
    # TODO: Create class and move methods inside class so 
    #       that common variables like home, etc. can be abstracted
    print "Installing apr"
    home = expanduser("~")
    libpath = home+"/lib/apr"
    prefix = "--prefix="+libpath
    arguments=[]
    arguments.append(prefix)
    configure_make_install(apr_path, arguments)

def install_apr_util(apr_util_path, apr_path):
    print "Installing apr-util"
    home = expanduser("~")
    libpath = home+"/lib/apr-util"
    # TODO: Is there a better way to denote the arguments, 
    #       rather than string concat?
    prefix = "--prefix=" + libpath
    with_apr = "--with-apr=" + home + "/lib/apr" 
    arguments=[]
    arguments.append(prefix)
    arguments.append(with_apr)
    configure_make_install(apr_util_path, arguments)

def install_pcre(pcre_path):
    print "Installing pcre"
    home = expanduser("~")
    libpath = home+"/lib/pcre"
    prefix = "--prefix="+libpath
    arguments=[]
    arguments.append(prefix)
    configure_make_install(pcre_path, arguments)

def install_httpd(httpd_path, apr_path, apr_util_path, pcre_path):
    print "Installing httpd"
    home = expanduser("~")
    # TODO: Remove hard coded path
    libpath = home+"/apache"
    prefix = "--prefix="+libpath
    with_apr = "--with-apr=" + home + "/lib/apr"
    with_apr_util = "--with-apr-util=" + home + "/lib/apr-util"
    with_pcre = "--with-pcre=" + home + "/lib/pcre"
    arguments=[]
    arguments.append(prefix)
    arguments.append(with_apr)
    arguments.append(with_apr_util)
    arguments.append(with_pcre)
    configure_make_install(httpd_path, arguments)

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

def install_modules(config_filepath):
    # TODO: Add unit tests
    modules_dict = read_file(config_filepath)
    download_modules(modules_dict)
    extract_modules(modules_dict)

    apr_path = get_folder_path(modules_dict, "apr")
    install_apr(apr_path)

    apr_util_path = get_folder_path(modules_dict, "apr-util")
    install_apr_util(apr_util_path, apr_path)

    pcre_path = get_folder_path(modules_dict, "pcre")
    install_pcre(pcre_path)
    
    httpd_path = get_folder_path(modules_dict, "httpd")
    install_httpd(httpd_path, apr_path, apr_util_path, pcre_path)

def update_listen_port(old_port, new_port, apache_install_path):
    conf_filepath = apache_install_path + "/conf/httpd.conf"
    # TODO: Fails when called twice, look for end of line in seach sequence
    pattern="Listen "+old_port
    subst="Listen "+new_port
    fh, abs_path = mkstemp()
    new_file = open(abs_path,'w')
    old_file = open(conf_filepath)
    for line in old_file:
        new_file.write(line.replace(pattern, subst))
    new_file.close()
    close(fh)    
    old_file.close()

    remove(conf_filepath)
    move(abs_path, conf_filepath) 

def start_apache(apache_install_path):
    apachectl_path = apache_install_path + "/bin/apachectl"
    call([apachectl_path, "-k", "restart"])

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
apache_install_path=home+"/apache"
install_modules("download_config")
update_listen_port("80", "8080", apache_install_path)
start_apache(apache_install_path)
cleanup(existing_files)
