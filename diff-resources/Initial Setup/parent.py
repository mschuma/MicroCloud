#Socket client example in python

import socket   #for sockets
import sys      #for exit

#create an INET, STREAMing socket
try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
        print 'Failed to create socket'
        sys.exit()


if len (sys.argv) != 2:
    print "Usage: python parent.py <child ip address> "
    sys.exit (1)

host = sys.argv[1];

port = 9888;

try:
        remote_ip = socket.gethostbyname( host )

except socket.gaierror:
        #could not resolve
        print 'Hostname could not be resolved. Exiting'
        sys.exit()

#Connect to remote server
for port in (8888,8900):
    try:
      s.connect((remote_ip , port))
      break
    except socket.error, msg:
      sys.exit()


#Send some data to remote server
message = "User Creation"

try :
        #Set the whole string
        s.sendall(message)
except socket.error:
        #Send failed
        print 'Send failed'
        sys.exit()



reply = s.recv(1024)

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
reply = s.recv(1024)

if reply == "Sending Key File":
        print 'Sending File'
        recvd = ''
        while True:
                reply = ''
                size = int(s.recv(16))
                s.sendall("ready")
                recvd = s.recv(size,socket.MSG_WAITALL)
                if len(recvd) == size:
                        fileWrite = open('/etc/vcl/lab.key','w+')
                        fileWrite.write(recvd)
                        break

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
fileRead.close()


while True:
        s.sendall("%16d"%len(data))
        reply =s.recv(1024)
        if reply == "ready":
                s.sendall(data)
                break


s.sendall("sending vclclientd")
reply = s.recv(1024)
if reply == "Ready":
        f = open('/usr/local/vcl/bin/vclclientd', "rb")
        while True:
                data = ''
                reply = ''
                data = f.read()
                s.sendall("%16d"%len(data))
                reply = s.recv(1024)
                if reply == "ready":
                        s.sendall(data)
                        break

reply = s.recv(1024)
if reply == "ready":
        s.sendall("sending S99vclclient")

reply = s.recv(1024)
if reply == "Ready":
        f = open('/usr/local/vcl/bin/S99vclclient.linux', "rb")
        while True:
                data = ''
                reply = ''
                data = f.read()
                print 'Length'
                print len(data)
                s.sendall("%16d"%len(data))
                reply = s.recv(1024)
                if reply == "ready":
                        s.sendall(data)
                        break


s.close()
