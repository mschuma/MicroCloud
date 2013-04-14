package edu.ncsu.csc.microcloud.daemon.parent;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.sql.Connection;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

import edu.ncsu.csc.microcloud.daemon.Constants;
import edu.ncsu.csc.microcloud.daemon.DBHelper;
import edu.ncsu.csc.microcloud.daemon.PropertiesHelper;
import edu.ncsu.csc.microcloud.daemon.ResourceRegistration;

public class ParentDaemon {
    private static final String CLASS_NAME = ParentDaemon.class.getCanonicalName();
    private final static List<String> children = new ArrayList<String>();

    static {
        //When the parent restarts, load all the children from the DB
        try {
            List<String> resources = ResourceRegistration.getChildren();
            System.out.println("Resources at startup :: " + resources);
            for (String child : resources) {
                addChild(child);
            }
        } catch (Exception ex) {
            ex.printStackTrace();
        }

    }

    /**
     * @param args
     */
    public static void main(String[] args) throws IOException {
        ServerSocket listener = null;
        try {
            Properties properties = PropertiesHelper.getParentProperties();
            listener = new ServerSocket(Integer.parseInt(properties.getProperty(Constants.PARENT_PORT, Constants.DEFAULT_PARENT_PORT)));
            System.out.println("Waiting for connections");
            long pollingPeriod = Long.parseLong(properties.getProperty(Constants.POLLING_PERIOD, Constants.DEFAULT_POLLING_PERIOD).trim());
            int childPort = Integer.parseInt(properties.getProperty(Constants.CHILD_PORT, Constants.DEFAULT_CHILD_PORT).trim());
            Thread poller = new Thread(new Poller(pollingPeriod, childPort));
            poller.start();
            while (true) {
                Socket socket = listener.accept();
                Thread t = new Thread(new ParentDaemonThread(socket, pollingPeriod));
                t.start();
            }
        } finally {
            if (listener != null) {
                listener.close();
            }
        }
    }

    public static synchronized void addChild(String child) {
        if (children != null && !children.contains(child)) {
            children.add(child);
        }
    }

    public static synchronized void removeChild(String child) {
        if (children != null) {
            children.remove(child);
        }
    }

    public static synchronized List<String> getChildren() {
        ArrayList<String> clone = new ArrayList<String>();
        for (String child : children) {
            clone.add(child);
        }
        return clone;
    }


}