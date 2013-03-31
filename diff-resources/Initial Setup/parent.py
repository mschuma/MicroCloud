#Socket client example in python

import socket   #for sockets
import sys      #for exit

#create an INET, STREAMing socket
try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
        print 'Failed to create socket'
        sys.exit()

print 'Socket Created'

host = '152.46.19.140';
port = 8888;

try:
        remote_ip = socket.gethostbyname( host )

except socket.gaierror:
        #could not resolve
        print 'Hostname could not be resolved. Exiting'
        sys.exit()

#Connect to remote server
s.connect((remote_ip , port))

print 'Socket Connected to ' + host + ' on ip ' + remote_ip

#Send some data to remote server
message = "User Creation"

try :
        #Set the whole string
        s.sendall(message)
except socket.error:
        #Send failed
        print 'Send failed'
        sys.exit()

print 'Message send successfully'

#Now receive data
reply = s.recv(4096)

if reply == "User OK":
        print "User Created"
if reply == "User present":
        print "vclstaff: User already present"

#Send some data to remote server
message = "Create SSH-Keygen"

try :
        #Set the whole string
        s.sendall(message)
except socket.error:
        #Send failed
        print 'Send failed'
        sys.exit()

		
		
		
#Now receive data
reply = s.recv(4096)

if reply == "Sending Key File":
        print 'Sending File'
        reply = s.recv(4096)
        fileWrite = open('/etc/vcl/dummylab.key','w+')
        fileWrite.write(reply)

VCLCONFFILE = open('/etc/vcl/vcld.conf','a+b')
VCLCONFFILE.write('\n')
VCLCONFFILE.write('IDENTITY_solaris_lab=/etc/vcl/lab.key')
VCLCONFFILE.write('\n')
VCLCONFFILE.write('IDENTITY_linux_lab=/etc/vcl/lab.key')
VCLCONFFILE.close()


#Send some data to remote server
message = "Sending SSHD File"

try :
        #Set the whole string
        s.sendall(message)
except socket.error:
        #Send failed
        print 'Send failed'
        sys.exit()

fileRead = open('vcl_sshd','rb')
data = fileRead.read()

try :
        #Set the whole string
        s.sendall(data)
except socket.error:
        #Send failed
        print 'Send failed'
        sys.exit()


s.close()
		
