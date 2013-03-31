package edu.ncsu.csc.microcloud.daemon.child;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.Properties;

import org.json.simple.JSONObject;

import edu.ncsu.csc.microcloud.daemon.Constants;
import edu.ncsu.csc.microcloud.daemon.PropertiesHelper;

public class ChildDaemon {

	private static final String CLASS_NAME = ChildDaemon.class.getCanonicalName();	

	/**
	 * @param args
	 */
	public static void main(String[] args) {		
		try{			
			connectToParent();
			listenToIsAlive();
		}catch(IOException ex){
			System.out.println("Exception @ : " + CLASS_NAME);
			ex.printStackTrace();
		}
	}

	private static void listenToIsAlive() throws IOException{
		Properties properties = PropertiesHelper.getProperties();
		String child_port = properties.getProperty(Constants.CHILD_PORT, Constants.DEFAULT_CHILD_PORT).trim();
		ServerSocket listener = new ServerSocket(Integer.parseInt(child_port));
		try{
			while(true){
				Socket socket = listener.accept();
				try{
					/*BufferedReader buffer = new BufferedReader(new InputStreamReader(listener.getInputStream()));
				if(buffer.readLine().equals(Constants.MSG_IS_ALIVE)){
					PrintWriter outputStream = new PrintWriter(listener.getOutputStream(), true);
					outputStream.println(Constants.OK_MESSAGE);	
				}*/
				}finally{
					socket.close();

				}
			}
		}finally{
			listener.close();
		}
	}

	private static void connectToParent() throws IOException{
		Properties properties = PropertiesHelper.getProperties();
		String parent_ip = properties.getProperty(Constants.PARENT_IP, Constants.DEFAULT_PARENT_IP).trim();
		String parent_port = properties.getProperty(Constants.PARENT_PORT, Constants.DEFAULT_PARENT_PORT).trim();
		Socket client = new Socket(parent_ip, Integer.parseInt(parent_port));
		JSONObject json = new JSONObject();
		json.put(Constants.MSG_TYPE, Constants.MSG_TYPE_REGISTER);
		BufferedReader reader = new BufferedReader(new InputStreamReader(client.getInputStream()));
		PrintWriter writer = new PrintWriter(new OutputStreamWriter(client.getOutputStream()), true);
		try{
			if(reader != null && writer != null){
				//send the connect message to the server
				String message = null;
				while((message = reader.readLine()) != null){
					if(message.equalsIgnoreCase(Constants.OK_MESSAGE)){
						writer.println(json.toJSONString());
						break;
					}
				}

				//Wait for the server to send the ok message
				while((message = reader.readLine()) != null){					
					if(message.equalsIgnoreCase(Constants.OK_MESSAGE)){
						break;
					}
				}				

			}
		}finally{
			reader.close();
			writer.close();
			client.close();
		}

	}

}
