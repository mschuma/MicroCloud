package edu.ncsu.csc.microcloud.daemon.child;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.Socket;
import java.util.Properties;

public class ChildDaemon {
	
	private static final String CLASS_NAME = ChildDaemon.class.getCanonicalName();
	/**
	 * @param args
	 */
	public static void main(String[] args) throws IOException{		
		Properties properties = new Properties();
		properties.load(new FileReader(new File("child_config.properties")));
		String parent_ip = properties.getProperty("parent_ip", "localhost").trim();
		String parent_port = properties.getProperty("parent_port", "9000").trim();
		Socket client = new Socket(parent_ip, Integer.parseInt(parent_port));
		BufferedReader reader = new BufferedReader(new InputStreamReader(client.getInputStream()));
		try{
			System.out.println(reader.readLine());
		}finally{
			reader.close();
			client.close();
		}
	}

}
