package edu.ncsu.csc.microcloud.daemon.parent;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;
import java.util.Properties;

import edu.ncsu.csc.microcloud.daemon.Constants;

public class ParentDaemon {
	private static final String CLASS_NAME = ParentDaemon.class.getCanonicalName();
	private static ArrayList<String> children = new ArrayList<String>();
	private static Properties properties;

	static {
		try{
			properties = new Properties();
			properties.load(new FileReader(new File(Constants.CONFIG_FILE)));
		}catch(IOException  ex){
			System.out.println("Exception while loading the property file @ : " + CLASS_NAME);
			ex.printStackTrace();
		}
	}
	/**
	 * @param args
	 */
	public static void main(String[] args) throws IOException{
		ServerSocket listener = null;
		try{
			
			listener = new ServerSocket(Integer.parseInt(properties.getProperty(Constants.PARENT_PORT, Constants.DEFAULT_PARENT_PORT)));
			System.out.println("Waiting for connections");
			int pollingPeriod = Integer.parseInt(properties.getProperty(Constants.POLLING_PERIOD, Constants.DEFAULT_POLLING_PERIOD).trim());
			int childPort = Integer.parseInt(properties.getProperty(Constants.CHILD_PORT, Constants.DEFAULT_CHILD_PORT).trim());
			Thread poller = new Thread(new Poller(pollingPeriod, childPort));
			poller.start();
			while(true){
				Socket socket = listener.accept();
				Thread t = new Thread(new ParentDaemonThread(socket));
				t.start();
			}
		}finally{
			listener.close();
		}
	}

	public static synchronized void addChild(String child){
		if(children != null && !children.contains(child)){
			children.add(child);
		}
	}

	public static synchronized void removeChild(String child){
		if(children != null){
			children.remove(child);
		}
	}
	
	public static synchronized ArrayList<String> getChildren(){
		return children;
	}
	
	public static synchronized void setChildren(ArrayList<String> childrenList){
		children = childrenList;
	}
}