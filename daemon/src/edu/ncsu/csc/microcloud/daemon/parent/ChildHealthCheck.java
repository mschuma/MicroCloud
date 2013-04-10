package edu.ncsu.csc.microcloud.daemon.parent;

import java.io.IOException;
import java.net.Socket;

import edu.ncsu.csc.microcloud.daemon.Constants;
import edu.ncsu.csc.microcloud.daemon.PropertiesHelper;
import edu.ncsu.csc.microcloud.daemon.ResourceRegistration;

public class ChildHealthCheck implements Runnable{

	private static long CONNECTION_RETRY_TIME;
	private static int CONNECTION_RETRIES_ALLOWED;

	static{
		String connectionRetriesAllowed = PropertiesHelper.getParentProperties().getProperty(Constants.CONNECTION_RETRIES_ALLOWED,
				Constants.DEFAULT_CONNECTION_RETRIES_ALLOWED).trim();

		String connectionRetryTime = PropertiesHelper.getParentProperties().getProperty(Constants.CONNECTION_RETRY_TIME,
				Constants.DEFAULT_CONNECTION_RETRY_TIME).trim();
		try{

			CONNECTION_RETRIES_ALLOWED = Integer.parseInt(connectionRetriesAllowed);
		}catch(NumberFormatException ex){
			System.out.println("number format exception for the property :: " + Constants.CONNECTION_RETRIES_ALLOWED);
			System.out.println("Its value is :: " + connectionRetriesAllowed);
			ex.printStackTrace();
			System.exit(-1);		
		}

		try{

			CONNECTION_RETRY_TIME = Long.parseLong(connectionRetryTime);
		}catch(NumberFormatException ex){
			System.out.println("number format exception for the property :: " + Constants.CONNECTION_RETRY_TIME);
			System.out.println("Its value is :: " + connectionRetryTime);
			ex.printStackTrace();
			System.exit(-1);			
		}
	}

	private String child;
	private int childPort;

	public ChildHealthCheck(String child, int childPort){
		this.child = child;
		this.childPort = childPort;
	}

	@Override
	public void run(){
		int attemptId = 1;
		boolean connected = false;
		Socket childSocket = null;
		try{
			while(!connected && attemptId <= CONNECTION_RETRIES_ALLOWED){
				try{
					childSocket = new Socket(this.child, this.childPort);
					connected = true;
					System.out.println("Child " + this.child + " is still alive");
				}catch(Exception ex){
					//ex.printStackTrace();								
					System.out.println("Ping attempt number " + attemptId + " for child " + this.child + " is unsuccessful");
					attemptId++;
					try{
						Thread.sleep(CONNECTION_RETRY_TIME);
					}catch(InterruptedException iex){
						iex.printStackTrace();
					}
				}							
			}
			if(!connected){
				//unregister the child
				System.out.println("Child " + child + "is dead. Deregistering....");
				ParentDaemon.removeChild(child);
				ResourceRegistration.unregisterResource(child);
			}
		}catch(Exception ex){
			ex.printStackTrace();
		}finally{
			if(childSocket != null){
				try{
					childSocket.close();
				}catch(IOException ex){
					ex.printStackTrace();
				}
			}
		}
	}

}
