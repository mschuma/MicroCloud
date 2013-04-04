package edu.ncsu.csc.microcloud.daemon.parent;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.Socket;
import java.util.Properties;

import org.json.simple.JSONObject;
import org.json.simple.JSONValue;

import edu.ncsu.csc.microcloud.daemon.Constants;
import edu.ncsu.csc.microcloud.daemon.ResourceRegistration;
import edu.ncsu.csc.microcloud.daemon.PropertiesHelper;

public class ParentDaemonThread implements Runnable {
	private static final String CLASS_NAME = ParentDaemonThread.class.getCanonicalName();
	private Socket socket;
	
	public ParentDaemonThread(Socket socket) {
		this.socket = socket;		
		
	}

	@Override
	public void run(){
		try{
			System.out.println("Communication from child :: " + socket.getInetAddress());
			BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
			PrintWriter writer = new PrintWriter(new OutputStreamWriter(socket.getOutputStream()), true);
			writer.println(Constants.OK_MESSAGE);
			String message = null;
			while((message = reader.readLine()) != null){
				JSONObject json = (JSONObject) JSONValue.parse(message);
				String msgType = (String)json.get(Constants.MSG_TYPE);
				if(msgType.equals(Constants.MSG_TYPE_REGISTER)){
                    invokeParentScript();                
					registerResource();
				}else if(msgType.equals(Constants.MSG_TYPE_UNREGISTER)){
					unregisterResource();
				}
				break;
			}
			
			
		}catch(IOException ex){
			System.out.println("Exception while talking to the client @ " + CLASS_NAME);
			ex.printStackTrace();
		}finally{
			try{
				socket.close();
			}catch(IOException ex){
				ex.printStackTrace();
			}
		}
	}

    private static void invokeParentScript() {
        Properties properties = PropertiesHelper.getParentProperties();
        String script_path = properties.getProperty(
                                Constants.PARENT_SCRIPT_PATH,
                                Constants.DEFAULT_PARENT_SCRIPT_PATH).trim();

        try {               
                Runtime.getRuntime().exec(
                    new String[] { "python", script_path, "&" });
            } catch (Exception ex) {
                System.out.println("Unable to start parent script");
                ex.printStackTrace();
        }
    }


	private void unregisterResource() throws IOException{
		//TODO: invoke the registration API
		String childIP = this.socket.getInetAddress().getHostAddress();
		ResourceRegistration.unregisterResource(childIP);
		ParentDaemon.removeChild(childIP);
		acknowledge();
	}

	private void registerResource() throws IOException{
		//TODO: invoke the registration API
		String childIP = this.socket.getInetAddress().getHostAddress();
		ResourceRegistration.registerResource(childIP);
		ParentDaemon.addChild(childIP);
		acknowledge();
	}
	
	private void acknowledge() throws IOException{
		PrintWriter outputStream = new PrintWriter(socket.getOutputStream(), true);
		outputStream.println(Constants.OK_MESSAGE);	
		outputStream.close();
	}

}
