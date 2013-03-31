import socket
import sys
import os

def runProcess(exe):
    p = subprocess.Popen(exe, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    while(True):
      retcode = p.poll() #returns None while subprocess is running
      line = p.stdout.readline()
      yield line
      if(retcode is not None):
        break

HOST = '0.0.0.0'        # Symbolic name meaning all available interfaces
PORT = 8888     # Arbitrary non-privileged port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'

for PORT in (8888,8900):
	try:
        s.bind((HOST, PORT))
		break
	except socket.error , msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
	

print 'Socket bind complete'
s.listen(10)
print 'Socket now listening'

#wait to accept a connection - blocking call
conn, addr = s.accept()

#display client information
print 'Connected with ' + addr[0] + ':' + str(addr[1])

#now keep talking with the client
data = conn.recv(1024)

if data == "User Creation":
        val =  runProcess("id -u vclstaff")
        if ( val <= 0):
                print 'came inside atleast'
                if runProcess("sudo /usr/sbin/useradd -d /home/vclstaff -m vclstaff")>0:
                        conn.sendall("User OK")
                else:
                        conn.sendall("User not Created")
        else:
                conn.sendall("User present")

#now keep talking with the client
data = conn.recv(1024)

if data == "Create SSH-Keygen":
        runProcess("ssh-keygen -t rsa -P '' -f 'vclstaff'")
        print 'SSH-Keygen'


		
os.system("cat vclstaff.pub >> /home/vclstaff/.ssh/authorized_keys")

f = open('vclstaff', "rb")
data = f.read()
f.close()

conn.sendall("Sending Key File")
conn.sendall(data)

data = conn.recv(1024)
if data ==  "Sending SSHD File":
        data == conn.recv(4096)
        fileWrite = open('/etc/ssh/vcl_sshd','w+')
        fileWrite.write(data)




conn.close()
s.close()
