package edu.ncsu.csc.microcloud.daemon.parent;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import javax.net.ssl.SSLSocket;

import org.json.simple.JSONObject;
import org.json.simple.JSONValue;

import edu.ncsu.csc.microcloud.daemon.Constants;
import edu.ncsu.csc.microcloud.daemon.ResourceRegistration;

public class ChildRegistrationThread implements Runnable {
	private static final String CLASS_NAME = ChildRegistrationThread.class.getCanonicalName();
	private SSLSocket socket;
    private final long pollingPeriod;
	
	public ChildRegistrationThread(SSLSocket socket, long pollingPeriod) {
		this.socket = socket;
        this.pollingPeriod = pollingPeriod;
	}

	@Override
	public void run(){
		try{
			System.out.println("Communication from child :: " + socket.getInetAddress());
			BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
			PrintWriter writer = new PrintWriter(new OutputStreamWriter(socket.getOutputStream()), true);
			writer.println(Constants.OK_MESSAGE);
            System.out.println("Sent OK message to :: " + socket.getInetAddress());
			String message = null;
			while((message = reader.readLine()) != null){
                System.out.println("Received registration message from :: " + socket.getInetAddress());
				JSONObject json = (JSONObject) JSONValue.parse(message);
				String msgType = (String)json.get(Constants.MSG_TYPE);
				if(msgType.equals(Constants.MSG_TYPE_REGISTER)){
                    System.out.println("Register child with VCL :: " + socket.getInetAddress());
					registerResource();
                    System.out.println("Finished registering child with VCL :: " + socket.getInetAddress());
				}else if(msgType.equals(Constants.MSG_TYPE_UNREGISTER)){
                    System.out.println("Unregister child from VCL :: " + socket.getInetAddress());
					unregisterResource();
                    System.out.println("Finished unregistering child with VCL :: " + socket.getInetAddress());
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

	private void unregisterResource() throws IOException{
		String childIP = this.socket.getInetAddress().getHostAddress();
		ResourceRegistration.unregisterResource(childIP);
		ParentDaemon.removeChild(childIP);
		acknowledge();
	}

	private void registerResource() throws IOException{
		String childIP = this.socket.getInetAddress().getHostAddress();
		ResourceRegistration.registerResource(childIP);
		ParentDaemon.addChild(childIP);
		acknowledge();
	}
	
	private void acknowledge() throws IOException{
        System.out.println("Sending acknowledgement to child :: " + socket.getInetAddress());
		PrintWriter outputStream = new PrintWriter(socket.getOutputStream(), true);
        JSONObject json = new JSONObject();
        json.put(Constants.MSG_TYPE, Constants.MSG_TYPE_ACKNOWLEDGE);
        json.put(Constants.POLLING_PERIOD, pollingPeriod );
		outputStream.println(json.toJSONString());
		outputStream.close();
        System.out.println("Finished sending acknowledgement to child :: " + socket.getInetAddress());
	}

}
