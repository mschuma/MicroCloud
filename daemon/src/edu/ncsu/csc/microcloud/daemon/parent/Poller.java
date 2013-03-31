package edu.ncsu.csc.microcloud.daemon.parent;

import java.net.Socket;
import java.util.ArrayList;
import java.util.List;

import edu.ncsu.csc.microcloud.daemon.ResourceRegistration;

public class Poller implements Runnable{
	private int pollingPeriod;
	private int childPort;

	public Poller(int pollingPeriod, int childPort) {
		this.pollingPeriod = pollingPeriod;
		this.childPort = childPort;
	}
	public void run(){
		while(true){
			try{
				Thread.sleep(this.pollingPeriod);
				List<String> children = ParentDaemon.getChildren();
				ArrayList<String> newChildren = new ArrayList<String>();
				if(children != null && children.size() > 0){
					Socket childSocket = null;					
					for(String child : children){
						try{
							childSocket = new Socket(child, this.childPort);
							System.out.println("Child " + child + " is still alive");
							newChildren.add(child);
						}catch(Exception ex){
							//ex.printStackTrace();
							//unregister the child
							System.out.println("Child " + child + " is dead");
							ResourceRegistration.unregisterResource(child);
						}finally{
							if(childSocket != null){
								childSocket.close();
							}
						}
					}
				}
				ParentDaemon.setChildren(newChildren);
			}catch(Exception ex){
				ex.printStackTrace();
			}
		}
	}
}
