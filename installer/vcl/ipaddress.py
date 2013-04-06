#!/usr/bin/python

import sys
import netifaces as ni
import socket, struct

class IPAddress:
    @staticmethod
    def get_private_ip_address():
        private_interfaces = dict()
    
        for interface in ni.interfaces():
            address = ni.ifaddresses(interface)
            if (address is not None and 
                ni.AF_INET in address and 
                len(address[ni.AF_INET]) > 0 and
                'addr' in address[ni.AF_INET][0]):
                ip_address = address[ni.AF_INET][0]['addr']
                if IPAddress.is_private_ip_address(ip_address):
                    private_interfaces[interface] = ip_address
    
        if len(private_interfaces) < 1:
            print "No private interfaces found"
            sys.exit(1)
    
        if len(private_interfaces) > 1:
            print "Found multiple private interfaces"
    
        ip_address = private_interfaces[private_interfaces.keys()[0]]
        print "Using IP address : " + ip_address
    
        return ip_address
    
    @staticmethod
    def is_private_ip_address(ip_address):
        private_ip_addresses = dict()
        private_ip_addresses["classC_start"] = \
                                IPAddress.convert_aton_ip("192.168.0.0")
        private_ip_addresses["classC_end"] = \
                                IPAddress.convert_aton_ip("192.168.255.255")
        private_ip_addresses["classB_start"] = \
                                IPAddress.convert_aton_ip("172.16.0.0")
        private_ip_addresses["classB_end"] = \
                                IPAddress.convert_aton_ip("172.31.255.255")
        private_ip_addresses["classA_start"] = \
                                IPAddress.convert_aton_ip("10.0.0.0")
        private_ip_addresses["classA_end"] = \
                                IPAddress.convert_aton_ip("10.255.255.255")
    
        ip = IPAddress.convert_aton_ip(ip_address)
    
        is_classA = (ip >= private_ip_addresses["classA_start"] and 
                        ip <= private_ip_addresses["classA_end"])
        is_classB = (ip >= private_ip_addresses["classB_start"] and 
                        ip <= private_ip_addresses["classB_end"])
        is_classC = (ip >= private_ip_addresses["classC_start"] and 
                        ip <= private_ip_addresses["classC_end"])
    
        return is_classA or is_classB or is_classC
    
    @staticmethod
    def convert_aton_ip(ip_address):
        return struct.unpack("!L", socket.inet_aton(ip_address))[0]
