package edu.ncsu.csc.microcloud.daemon.parent;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;

public class ParentDaemon {
	private static final String CLASS_NAME = ParentDaemon.class.getCanonicalName();
	/**
	 * @param args
	 */
	public static void main(String[] args) throws IOException{
		ServerSocket listener = null;
		try{
			listener = new ServerSocket(9000);
			System.out.println("Waiting for connections");
			while(true){
				Socket socket = listener.accept();
				Thread t = new Thread(new ParentDaemonThread(socket));
				t.start();
			}
		}finally{
			listener.close();
		}

	}
}