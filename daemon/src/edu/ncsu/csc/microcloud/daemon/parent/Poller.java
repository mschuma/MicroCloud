package edu.ncsu.csc.microcloud.daemon.parent;

import java.util.List;

public class Poller implements Runnable{
	private long pollingPeriod;
	private int childPort;


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
					for(String child : children){
						Thread childHealthCheck = new Thread(new ChildHealthCheck(child, childPort));
						childHealthCheck.start();
					}
				}
			}catch(Exception ex){
				ex.printStackTrace();
			}
		}
	}
}
