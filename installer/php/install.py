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

def install_modules(config_filepath):
    # TODO: Move common methods to utility library
    # TODO: Add unit tests
    modules_dict = read_file(config_filepath)
    download_modules(modules_dict)
    extract_modules(modules_dict)

install_modules("pre_requisites")
install_modules("main")
install_modules("post_main")
