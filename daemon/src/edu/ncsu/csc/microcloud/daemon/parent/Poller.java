package edu.ncsu.csc.microcloud.daemon.parent;

import java.util.List;
import java.util.concurrent.Executor;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

public class Poller implements Runnable{
	private long pollingPeriod;
	private int childPort;
    private Executor executor;


	public Poller(long pollingPeriod, int childPort) {
        executor = new ThreadPoolExecutor(2,2,5, TimeUnit.SECONDS, new LinkedBlockingQueue<Runnable>());
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
                        executor.execute(new ChildHealthCheck(child, childPort));
					}
				}
			}catch(Exception ex){
				ex.printStackTrace();
			}
		}
	}
}
