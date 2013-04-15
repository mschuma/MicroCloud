#!/bin/sh
java -cp parent_config.properties:parent_daemon.jar:dependencies/json-simple-1.1.1.jar:dependencies/mysql-connector-java-5.1.22-bin.jar  -Djavax.net.ssl.keyStore=mySrvKeystore -Djavax.net.ssl.keyStorePassword=vclroot -Djavax.net.ssl.trustStore=myCliKeystore -Djavax.net.ssl.trustStorePassword=vclroot edu.ncsu.csc.microcloud.daemon.parent.ParentDaemon
