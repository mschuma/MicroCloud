MicroCloud
==========

CSC-591-004 MicroCloud Project Repository

Creating Parent and Child Daemon JARS
-------------------------------------------
Update the build.properties file located under daemon/build dir.
Runt ant to build the jars.


Child Daemon
-------------------------------
The child daemon runs on port 9090 by default. This can be configured via the config.properties file. Make sure this port is open at the firewall.

Update config.properties file to set the parent ip address and port

Run the child daemon as follows:
			
java -cp <Config>:<Child_Jar>:<Json> edu.ncsu.csc.microcloud.daemon.child.ChildDaemon



Parent Daemon
--------------------------------------------------
The child daemon runs on port 9000 by default. This can be configured via the config.properties file. Make sure this port is open at the firewall.

Run the child daemon as follows:
			
java -cp <Config>:<Parent_Jar>:<Json>:<MySql> edu.ncsu.csc.microcloud.daemon.parent.ParentDaemon

where,
<Config> = Directory which contains the config.properties file
<Parent_Jar> = Parent Jar file path
<Child_Jar> = Child Jar file path
<MySql> = MySql Jar file path
<Json> = Json Jar file path


