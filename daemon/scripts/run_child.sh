 #!/bin/sh
java -cp child_config.properties:child_daemon.jar:dependencies/json-simple-1.1.1.jar -Djavax.net.ssl.trustStore=/home/vcluser/dist/mySrvKeystore -Djavax.net.ssl.trustStorePassword=vclroot -Djavax.net.ssl.keyStore=myCliKeystore -Djavax.net.ssl.keyStorePassword=vclroot edu.ncsu.csc.microcloud.daemon.child.ChildDaemon
