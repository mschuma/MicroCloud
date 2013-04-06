MicroCloud
==========

Scripted install for VCL according to the steps mentioned in the 
[VCL 2.3.1 Installation Guide][1]

Pre requisites
-----
The following modules are required for the script:
 1. MySQL: `yum install MySQL-python`
 2. netifaces: 
  1. `wget http://dl.fedoraproject.org/pub/epel/5/x86_64/epel-release-5-4.noarch.rpm`
  2. `rpm -Uvh epel-release*rpm`
  3. `yum install python-netifaces`

Usage
-----
`python install.py`

 [1]: http://vcl.apache.org/docs/VCL231InstallGuide.html
