#!/usr/bin/python

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

def configure_make_install_modules(modules_dict):
    print "Configuring modules"
    home = expanduser("~")
    libpath = home+"/lib"
    makefile_prefix="PREFIX="+libpath
    makefile_libpath ="LIB="+libpath
    
    arguments = ["perl"]
    arguments.append("Makefile.PL")
    arguments.append(makefile_prefix)
    arguments.append(makefile_libpath)

    for (module_name, url) in modules_dict.iteritems():
        # TODO: Check if the file exists 
        filename = url.split('/')[-1]
        folder_name = filename.strip(".tar.gz")
        configure_make_install(folder_name, arguments)

def configure_make_install(source_path, configure_arguments):
    saved_path = os.getcwd()
    os.chdir(source_path);

    call(configure_arguments)
    call("make")
    call(["make", "install"])

    os.chdir(saved_path)

def install_modules(config_filepath):
    # TODO: Add unit tests
    modules_dict = read_file(config_filepath)
    download_modules(modules_dict)
    extract_modules(modules_dict)
    configure_make_install_modules(modules_dict)

install_modules("pre_requisites")
install_modules("main")
install_modules("post_main")
