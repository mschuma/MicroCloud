#!/usr/bin/python

import urllib
import threading
import tarfile
import os
from subprocess import call
from os.path import expanduser

def read_file(filepath):
    f = open(filepath)
    lines = f.readlines()
    f.close

    return lines

def download_modules(readlines):
    for line in readlines:
        (module_name, url) = line.split( )
        #TODO: Check for errors
        filename = url.split('/')[-1]
        #TODO: Include checksum in config file to verify
        urllib.urlretrieve(url, filename)

def extract_modules(readlines):
    home = expanduser("~")
    libpath = home+"/lib"
    makefile_prefix="PREFIX="+libpath
    makefile_libpath ="LIB="+libpath
    saved_path = os.getcwd()
    
    for line in readlines:
        (module_name, url) = line.split( )
        # TODO: Check if the file exists 
        filename = url.split('/')[-1]
        tar = tarfile.open(filename)
        tar.extractall()
        tar.close()
        folder_name = filename.strip(".tar.gz")

        os.chdir(folder_name)
        call(["perl", "Makefile.PL", makefile_prefix, makefile_libpath])
        os.chdir(saved_path)

    os.chdir(saved_path)

def make_install_modules(readlines):
    saved_path = os.getcwd()
    
    for line in readlines:
        (module_name, url) = line.split( )
        # TODO: Check if the file exists 
        filename = url.split('/')[-1]
        folder_name = filename.strip(".tar.gz")

        os.chdir(folder_name)
        call("make")
        call(["make", "install"])
        os.chdir(saved_path)

    os.chdir(saved_path)

def install_modules(config_filepath):
    # TODO: Add unit tests
    readlines=read_file(config_filepath)
    download_modules(readlines)
    extract_modules(readlines)
    make_install_modules(readlines)

#install_modules("pre_requisites")
#install_modules("main")
install_modules("post_main")
