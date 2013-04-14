#!/bin/sh
java -cp child_config.properties:child_daemon.jar:dependencies/json-simple-1.1.1.jar edu.ncsu.csc.microcloud.daemon.child.ChildDaemon
