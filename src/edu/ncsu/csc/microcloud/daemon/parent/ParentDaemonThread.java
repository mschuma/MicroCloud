package edu.ncsu.csc.microcloud.daemon.parent;

import java.io.IOException;
import java.io.PrintWriter;
import java.net.Socket;

public class ParentDaemonThread implements Runnable {
	private static final String CLASS_NAME = ParentDaemonThread.class.getCanonicalName();
	private Socket socket;

	public ParentDaemonThread(Socket socket) {
		this.socket = socket;
	}

	@Override
	public void run(){
		try{
			System.out.println(socket.getInetAddress());
			PrintWriter outputStream = new PrintWriter(socket.getOutputStream(), true);
			outputStream.println(socket.getInetAddress());	
		}catch(IOException ex){
			System.out.println("Exception while talking to the client");
			ex.printStackTrace();
		}finally{
			try{
				socket.close();
			}catch(IOException ex){
				ex.printStackTrace();
			}
		}
	}

}
