package edu.ncsu.csc.microcloud.daemon.parent;

import java.net.Socket;
import java.util.List;

import edu.ncsu.csc.microcloud.daemon.Constants;
import edu.ncsu.csc.microcloud.daemon.PropertiesHelper;
import edu.ncsu.csc.microcloud.daemon.ResourceRegistration;

public class Poller implements Runnable{
	private long pollingPeriod;
	private int childPort;
	private static long CONNECTION_RETRY_TIME;
	private static int CONNECTION_RETRIES_ALLOWED;

	static{
		String connectionRetriesAllowed = PropertiesHelper.getParentProperties().getProperty(Constants.CONNECTION_RETRIES_ALLOWED,
				Constants.DEFAULT_CONNECTION_RETRIES_ALLOWED).trim();

		String connectionRetryTime = PropertiesHelper.getParentProperties().getProperty(Constants.CONNECTION_RETRIES_ALLOWED,
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

			CONNECTION_RETRY_TIME = Integer.parseInt(connectionRetryTime);
		}catch(NumberFormatException ex){
			System.out.println("number format exception for the property :: " + Constants.CONNECTION_RETRY_TIME);
			System.out.println("Its value is :: " + connectionRetryTime);
			ex.printStackTrace();
			System.exit(-1);			
		}
	}

	public Poller(long pollingPeriod, int childPort) {
		this.pollingPeriod = pollingPeriod;
		this.childPort = childPort;		
	}
	public void run(){
		while(true){
			try{
				Thread.sleep(this.pollingPeriod);
				List<String> children = ParentDaemon.getChildren();
				if(children != null && children.size() > 0){
					Socket childSocket = null;					
					for(String child : children){
						int attemptId = 1;
						boolean connected = false;
						while(!connected && attemptId <= CONNECTION_RETRIES_ALLOWED){
							try{
								childSocket = new Socket(child, this.childPort);
								connected = true;
								System.out.println("Child " + child + " is still alive");
							}catch(Exception ex){
								//ex.printStackTrace();								
								System.out.println("Ping attempt number " + attemptId + " for child " + child + " is unsuccessful");
							}
							attemptId++;
							Thread.sleep(CONNECTION_RETRY_TIME);
						}
						if(!connected){
							//unregister the child
							System.out.println("Child " + child + "is dead. Deregistering....");
							ParentDaemon.removeChild(child);
							ResourceRegistration.unregisterResource(child);
						}

						if(childSocket != null){
							childSocket.close();
						}
					}
				}
			}catch(Exception ex){
				ex.printStackTrace();
			}
		}
	}
}
