#!/usr/bin/python

import os
import shutil
import md5
import random
import string

# TODO: Can be made singleton
class Utilities:    
    @staticmethod
    def read_file(filepath):
        if not Utilities.file_exists(filepath):
            return        
            
        modules = dict()
        for line in open(filepath):
            key, value = line.split()
            modules[key.strip()] = value.strip() 

        return modules        

    @staticmethod
    def file_exists(filepath):
        try:
            file_handler = open(filepath)
            file_handler.close()
        except IOError:            
            return False
        return True
    
    @staticmethod
    def verify_md5(tar_filepath, md5_filepath):    
        if not Utilities.file_exists(tar_filepath):
            print "tar file does not exist at " + tar_filepath             
            return False
        
        if not Utilities.file_exists(md5_filepath):
            print "tar file does not exist at " + md5_filepath
            return False
        
        md5_actual = md5.new(open(tar_filepath, "rb").read()).hexdigest()
        md5_expected = open(md5_filepath, "rb").read().split(' ')[0]
    
        print "Comparing MD5 hashes"
        if md5_actual == md5_expected:
            print "MD5 Checksum verified"
            return True
    
        print "MD5 Checksum does not match"
        return False
    
    @staticmethod
    def cleanup(existing_files):
        folder = os.getcwd()
        for entry in os.listdir(folder):
            if entry in existing_files:
                continue            
            path = os.path.join(folder, entry)        
            if os.path.isfile(path):
                os.unlink(path)
                print "Deleted " + path
            elif os.path.isdir(path):
                print "Deleted " + path
                shutil.rmtree(path)
    
    @staticmethod
    def generate_random_text():
        random_chars = \
            "".join([random.choice(string.letters) for i in xrange(30)])
        return random_chars
    
    @staticmethod
    def is_package_installed(package_name):
        # TODO: Check if the specified package is installed        
        return True                
