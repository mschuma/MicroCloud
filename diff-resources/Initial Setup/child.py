import socket
import sys
import os

def runProcess(exe):
    # TODO: Kill the process after the diff resources has been setup
    p = subprocess.Popen(exe, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    while(True):
      retcode = p.poll() #returns None while subprocess is running
      line = p.stdout.readline()
      yield line
      if(retcode is not None):
        break

HOST = '0.0.0.0'        # Symbolic name meaning all available interfaces
PORT = 9888     # Arbitrary non-privileged port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


for PORT in (8888,8900):
   try:
        s.bind((HOST, PORT))
        break
   except socket.error , msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()


s.listen(10)


#wait to accept a connection - blocking call
conn, addr = s.accept()


#now keep talking with the client
data = conn.recv(1024)

if data == "User Creation":
        val =  runProcess("id -u vclstaff | grep 'no'")
        if ( val >= 0):
                print 'came inside atleast'
                if os.system("/usr/sbin/useradd -d /home/vclstaff -m vclstaff")>0:
                        conn.sendall("User OK")
                else:
                        conn.sendall("User not Created")
        else:
                conn.sendall("User present")

#now keep talking with the client
data = conn.recv(1024)

if data == "Create SSH-Keygen":
        os.system("ssh-keygen -t rsa -P '' -f '/home/vclstaff/vclstaff' -C 'vclstaff@'$HOSTNAME")
        print 'SSH-Keygen'



os.system("cat /home/vclstaff/vclstaff.pub >> /home/vclstaff/authorized_keys")

f = open('/home/vclstaff/vclstaff', "rb")
conn.sendall("Sending Key File")
while True:
        data = ''
        reply = ''
        data = f.read()
        conn.sendall("%16d"%len(data))
        reply = conn.recv(1024)
        if reply == "ready":
                conn.sendall(data)
                break

f.close()
data = conn.recv(1024)
if data ==  "Sending SSHD File":
        print data
        while True:
                reply = ''
                size = int(conn.recv(16))
                print size
                conn.sendall("ready")
                recvd = conn.recv(size,socket.MSG_WAITALL)
                if len(recvd) == size:
                        fileWrite = open('/home/vclstaff/vcl_sshd','w+')
                        fileWrite.write(recvd)
                        fileWrite.close()
                        break

# TODO: Does not retreive the remote address..,
remote_ip = socket.gethostbyname(socket.gethostname())
ListenAddress = 'ListenAddress '
ListenAddress += remote_ip
fileWrt = open('vcl_sshd','a+b')
fileWrt.write('\n')
fileWrt.write(ListenAddress)
fileWrt.write('\n')
fileWrt.close()


reply = conn.recv(1024)

if reply == "sending vclclientd":
        conn.sendall("Ready")
        recvd = ''
        while True:
                reply = ''
                size = int(conn.recv(16))
                conn.sendall("ready")
                recvd = conn.recv(size,socket.MSG_WAITALL)
                if len(recvd) == size:
                        fileWrite = open('vclclientd','w+')
                        fileWrite.write(recvd)
                        fileWrite.close()
                        break

conn.sendall("ready")
reply = conn.recv(1024)

if reply == "sending S99vclclient":
    conn.sendall("Ready")
    recvd = ''
    while True:
                reply = ''
                size = int(conn.recv(16))
                conn.sendall("ready")
                recvd = conn.recv(size,socket.MSG_WAITALL)
                if len(recvd) == size:
                        fileWrite = open('S99vclclient.linux','w+')
                        fileWrite.write(recvd)
                        fileWrite.close()
                        break

os.system("cp vclclientd /home/vclstaff")
os.system("chmod u=rwx /home/vclstaff/vclclientd")
os.system("cp S99vclclient.linux /etc/init.d")
os.system("chmod u=rwx /etc/init.d/S99vclclient.linux")
os.system("/etc/init.d/S99vclclient.linux start")
os.system("/usr/sbin/sshd -f vcl_sshd")
conn.close()
s.close()

