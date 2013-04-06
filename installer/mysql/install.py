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
import getpass
from os import remove, close
import subprocess

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

def install_cmake(cmake_path):
    # TODO: Create class and move methods inside class so 
    #       that common variables like home, etc. can be abstracted
    print "Installing cmake"
    home = expanduser("~")
    libpath = home+"/lib/cmake"
    prefix = "--prefix="+libpath
    arguments=[]
    arguments.append(prefix)
    configure_make_install("bootstrap", cmake_path, arguments)

def install_mysql(mysql_path, port_number):
    print "Installing mysqld"
    home = expanduser("~")
    # TODO: Remove hard coded path
    libpath = home+"/mysql"
    
    # Configure the source
    saved_path=os.getcwd()
    os.chdir(mysql_path)
    arguments=[]
    arguments.append(home+"/lib/cmake/bin/cmake")
    arguments.append("-DCMAKE_INSTALL_PREFIX="+libpath)
    arguments.append("-DMYSQL_TCP_PORT="+port_number)
    arguments.append("-DWITH_INNOBASE_STORAGE_ENGINE=1")
    arguments.append(".")
    call(arguments)
    call("make")
    call(["make", "install"])
    os.chdir(saved_path)

def configure_make_install(configure_filename, source_path, 
                                            configure_arguments):
    saved_path = os.getcwd()
    os.chdir(source_path);

    configure_arguments.insert(0, "./"+configure_filename)
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
    port_number = "3066"

    # TODO: Add unit tests
    modules_dict = read_file(config_filepath)
    download_modules(modules_dict)
    extract_modules(modules_dict)

    # TODO: Can be moved to the install method
    cmake_path = get_folder_path(modules_dict, "cmake")
    install_cmake(cmake_path)

    mysql_path = get_folder_path(modules_dict, "mysql")
    install_mysql(mysql_path, port_number)

def initialize_mysql(mysql_install_path, cnf_filepath, mysql_data_path, 
                            mysql_socket_path, port_number):
    username = getpass.getuser()

    print cnf_filepath
    # Remove existing cnf file
    if os.path.exists(cnf_filepath):
        remove(cnf_filepath)

    arguments = ["./mysql_install_db"]
    arguments.append("--user=" + username)
    arguments.append("--basedir=" + mysql_install_path)
    arguments.append("--datadir=" + mysql_data_path)
    arguments.append("--tmpdir=" + mysql_install_path + "/tmp")
    arguments.append("--socket=" + mysql_socket_path)
    arguments.append("--user="+username)

    saved_path = os.getcwd()
    os.chdir(mysql_install_path+"/scripts")
    call(arguments)
    os.chdir(saved_path)

    # Create cnf file
    f = open(cnf_filepath, "w")
    f.write("[mysqld]\n")
    f.write("user=" + username + os.linesep)
    f.write("basedir=" + mysql_install_path + os.linesep)
    f.write("datadir=" + mysql_data_path + os.linesep)
    f.write("socket=" + mysql_socket_path + os.linesep)
    f.write("port=" + port_number + os.linesep)
    f.close()

def start_mysqld(mysql_install_path, cnf_filepath, mysql_socket_path):
    saved_path = os.getcwd()
    os.chdir(mysql_install_path + "/bin")
    arguments=["./mysqld_safe"]
    arguments.append("--defaults-file=" + cnf_filepath)
    subprocess.Popen(arguments)
    os.chdir(saved_path)

def update_root_password(mysql_install_path, port_number, mysql_socket_path):
    saved_path = os.getcwd()
    os.chdir(mysql_install_path + "/bin")
    arguments=["./mysqladmin"]
    arguments.append("-u")
    arguments.append("root")
    arguments.append("-P")
    arguments.append(port_number)
    arguments.append("-S")
    arguments.append(mysql_socket_path)
    password = raw_input("Enter root password : ")
    arguments.append("password")
    arguments.append(password)
    subprocess.Popen(arguments)
    os.chdir(saved_path)

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

# TODO: Read from configuration file
#       Paths relative to the install path can be stored
mysql_install_path=home+"/mysql"
cnf_filepath = mysql_install_path + "/my.cnf"
mysql_datapath = home + "/mysql_data"
mysql_socket_path = mysql_install_path + "/tmp/mysql.sock"
# TODO: Should be a number (easier to validate)?
port_number="3066"

install_modules("download_config")
initialize_mysql(mysql_install_path, cnf_filepath, mysql_datapath, 
                        mysql_socket_path, port_number)
start_mysqld(mysql_install_path, cnf_filepath, mysql_socket_path)
#update_root_password(mysql_install_path, port_number, mysql_socket_path)
cleanup(existing_files)
