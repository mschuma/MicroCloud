#!/usr/bin/python

import urllib
import tarfile
import md5

from utilities import Utilities
from managementnodeinstaller import ManagementNodeInstaller
from databaseinstaller import DatabaseInstaller
from webserverinstaller import WebserverInstaller
from ipaddress import IPAddress

__ext__ = ".tar.bz2"

class ModuleProcessor:    
    VCL_KEY = "vcl"
    VCL_MD5_KEY = "vcl-md5"
    
    modules = None
    
    def __init__(self, config_filepath):
        self.modules = Utilities.read_file(config_filepath)

    @staticmethod
    def __verify_md5(tar_filepath, md5_filepath):        
        md5_verified = Utilities.verify_md5(tar_filepath, md5_filepath)
        if not md5_verified:
            return
        
        md5_actual = md5.new(open(tar_filepath, "rb").read()).hexdigest()
        md5_expected = open(md5_filepath, "rb").read().split(' ')[0]
    
        print "Comparing MD5 hashes"
        if md5_actual == md5_expected:
            print "MD5 Checksum verified"
            return True
    
        print "MD5 Checksum does not match"
        return False
    
    def __get_folder_path(self, module_name):
        filename = self.modules[module_name].split('/')[-1]
        if filename.endswith(__ext__):
            return filename[:-len(__ext__)]
    
    def __get_file_name(self, module_name):
        filename = self.modules[module_name].split('/')[-1]
        return filename

    def download(self):        
        if self.modules is None:
            print "No modules to download"
            return
         
        print "Downloading modules"
        for (module_name, url) in self.modules.iteritems():
            # TODO: Check for errors
            filename = url.split('/')[-1]
            # TODO: Include checksum in config file to verify
            # TODO: Pretty print in tabular format
            print "[%s] from %s ..." % (module_name, url)
            urllib.urlretrieve(url, filename)
    
        print "Completed downloading modules\n"
        
    def extract(self):
        if self.modules is None:
            print "No modules to extract"
            return
        
        print "Extracting modules"
        
        for (module_name, url) in self.modules.iteritems():
            # TODO: Can use key/value pair in the config file
            filename = url.split('/')[-1]
            if filename.endswith(__ext__) == False:
                continue
    
            print "[%s] from %s ..." % (module_name, filename)
            tar = tarfile.open(filename, "r:bz2")
    
            for member in tar.getmembers():
                tar.extract(member, "")
    
            tar.close()        
    
        print "Completed extracting modules\n"
    
    def install(self):
        # TODO: Add unit tests   
        self.download()
    
        tar_file_path = self.__get_file_name(self.VCL_KEY)
        md5_file_path = self.__get_file_name(self.VCL_MD5_KEY)
    
        md5_verified = ModuleProcessor.__verify_md5(tar_file_path,
                                                    md5_file_path)
        if not md5_verified:
            return
    
        self.extract()
        
        database_installer = DatabaseInstaller(
                                user_name="vcluser",
                                password="vcluserpassword",
                                webserver_ip_address="localhost",
                                webserver_port=80,
                                management_node_ip_address="localhost",
                                management_node_port=80) 
        database_installer.install()
        
        # TODO: Move value to configuration file or prompt user for input  
        # TODO: Move keys to constants module
        parameters = dict()
        parameters["database_name"] = "vcl"
        parameters["database_user"] = "vcluser"
        parameters["database_password"] = "vcluserpassword"
        parameters["hostname"] = "localhost"
        parameters["server_ip_address"] = IPAddress.get_private_ip_address()
        parameters["xmlrpc_password"] = "password"
        parameters["xmlrpc_url"] = \
                            ("https://%s/vcl/index.php?mode=xmlrpccall" % 
                            parameters["server_ip_address"])
    
        WebserverInstaller.install(
                        vcl_db=parameters["database_name"],
                        vcl_host=parameters["hostname"],
                        vcl_username=parameters["database_user"],
                        vcl_password=parameters["database_password"],
                        webserver_ip_address=parameters["server_ip_address"])
        
        # TODO: Move key names to constants module
        node_installer = ManagementNodeInstaller(
                        hostname=parameters["hostname"],
                        database_ip_address=parameters["server_ip_address"],
                        database_user=parameters["database_user"],
                        database_password=parameters["database_password"],
                        xmlrpc_password=parameters["xmlrpc_password"],
                        xmlrpc_url=parameters["xmlrpc_url"])
        node_installer.install()
