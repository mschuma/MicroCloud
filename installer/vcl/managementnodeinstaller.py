#!/usr/bin/python

import os
from subprocess import call
from tempfile import mkstemp
import shutil
from os import close

from utilities import Utilities

class ManagementNodeInstaller:
    VCLD_CONF_FILEPATH = "/etc/vcl/vcld.conf"
    SSH_CONF_FILEPATH = "/etc/ssh/ssh_config"
    
    parameters = dict()    
   
    # TODO: Encapsulate related arguments
    def __init__(self, hostname, database_ip_address,
                                            database_user, database_password,
                                            xmlrpc_password, xmlrpc_url):
        self.parameters["FQDN"] = hostname
        self.parameters["server"] = database_ip_address
        self.parameters["LockerWrtUser"] = database_user
        self.parameters["wrtPass"] = database_password
        self.parameters["xmlrpc_pass"] = xmlrpc_password
        self.parameters["xmlrpc_url"] = xmlrpc_url
            
    def install(self):
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
    
        self.update_ssh_conf()
        self.update_vcld_conf()
    
        # Set the vclsystem account password for xmlrpc api
        # call(["/usr/local/vcl/bin/vcld", "-setup"])
                           
    def update_ssh_conf(self):
        if not Utilities.file_exists(self.SSH_CONF_FILEPATH):
            print "ssh conf file does not exist at " + self.SSH_CONF_FILEPATH
            return
            
        # TODO: Check whether the entries exist before appending (for each host)
        conf_file = open(self.SSH_CONF_FILEPATH, 'a')
        conf_file.write("    UserKnownHostsFile /dev/null\n")
        conf_file.write("    StrictHostKeyChecking no\n")
        conf_file.close()
    
    def update_vcld_conf(self):
        if not Utilities.file_exists(self.VCLD_CONF_FILEPATH):
            print "vcld conf file does not exist at " + self.VCLD_CONF_FILEPATH
            return        
            
        file_handler, abs_path = mkstemp()
    
        old_file = open(self.VCLD_CONF_FILEPATH)
        temp_file = open(abs_path, 'w')
    
        for line in old_file:
            words = line.split('=')
            if len(words) <= 1:
                temp_file.write(line)
                continue
            
            key, value = line.split('=')
            if key.strip() not in self.parameters:
                temp_file.write(line)
                continue
    
            value = self.parameters[key.strip()]
            temp_file.write("%s=%s\n" % (key.strip(), value))
        
        old_file.close()
        temp_file.close()
        close(file_handler)
        
        # Copy from the temp file to secrets.php (so as not to loose the 
        # file permissions on secrets.php
        conf_file = open(self.VCLD_CONF_FILEPATH, 'w')
        temp_file = open(abs_path)
    
        for line in temp_file:
            conf_file.write(line)
    
        conf_file.close()
