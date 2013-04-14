package edu.ncsu.csc.microcloud.daemon.child;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketTimeoutException;
import java.util.Properties;

import org.json.simple.JSONObject;

import edu.ncsu.csc.microcloud.daemon.Constants;
import edu.ncsu.csc.microcloud.daemon.PropertiesHelper;
import org.json.simple.JSONValue;

public class ChildDaemon {

    private static final String CLASS_NAME = ChildDaemon.class.getCanonicalName();
    private static long CONNECTION_RETRY_TIME;
    private static int POLLING_PERIOD;

    static {
        String connectionRetryTime = PropertiesHelper.getChildProperties().getProperty(Constants.CONNECTION_RETRY_TIME,
                Constants.DEFAULT_CONNECTION_RETRY_TIME).trim();
        try {
            CONNECTION_RETRY_TIME = Long.parseLong(connectionRetryTime);
        } catch (NumberFormatException ex) {
            System.out.println("number format exception for the property :: " + Constants.CONNECTION_RETRY_TIME);
            System.out.println("Its value is :: " + connectionRetryTime);
            ex.printStackTrace();
            System.exit(-1);
        }
    }

    /**
     * @param args
     */
    public static void main(String[] args) {
        while (true) {
            try {
                connectToParent();
                listenToIsAlive();
            } catch (SocketTimeoutException ex){
                System.err.println("Parent hasn't phoned in a while, lets try reconnecting");
            }catch (IOException ex) {
                System.err.println("Exception @ : " + CLASS_NAME);
                ex.printStackTrace();
            }
        }
    }

    private static void listenToIsAlive() throws IOException {
        Properties properties = PropertiesHelper.getChildProperties();
        String child_port = properties.getProperty(Constants.CHILD_PORT, Constants.DEFAULT_CHILD_PORT).trim();
        ServerSocket listener = new ServerSocket(Integer.parseInt(child_port));
        listener.setSoTimeout(POLLING_PERIOD * 4);
        try {
            while (true) {
                Socket socket = null;
                try {
                    socket = listener.accept();
                } finally {
                    if (socket != null) {
                        socket.close();
                    }
                }
            }
        } finally {
            listener.close();
        }
    }

    private static void connectToParent() throws IOException {
        Properties properties = PropertiesHelper.getChildProperties();
        String parent_ip = properties.getProperty(Constants.PARENT_IP, Constants.DEFAULT_PARENT_IP).trim();
        String parent_port = properties.getProperty(Constants.PARENT_PORT, Constants.DEFAULT_PARENT_PORT).trim();

        System.out.println("Parent IP :: " + parent_ip);
        System.out.println("Parent port :: " + parent_port);

        boolean connected = false;
        int connectionAttempt = 1;
        Socket client = null;

        while (!connected) {
            try {
                client = new Socket(parent_ip, Integer.parseInt(parent_port));
                connected = true;
            } catch (Exception ex) {
                System.out.println("Attempt :: " + connectionAttempt + " => Unable to connect to the parent");
                ex.printStackTrace();
                try {
                    Thread.sleep(CONNECTION_RETRY_TIME);
                } catch (InterruptedException iex) {
                    System.out.println("Exception while child thread sleeps");
                    iex.printStackTrace();
                }
                connectionAttempt++;
            }

        }

        System.out.println("Attempt :: " + connectionAttempt + " => Successfully connected to the parent");

        BufferedReader reader = new BufferedReader(new InputStreamReader(client.getInputStream()));
        PrintWriter writer = new PrintWriter(new OutputStreamWriter(client.getOutputStream()), true);
        try {
            if (reader != null && writer != null) {
                if (readOkMessage(reader)) {
                    writeRegisterMessage(writer);
                }

                POLLING_PERIOD = (int) readAcknowledgementAndPollingPeriod(reader);
            }
        } finally {
            reader.close();
            writer.close();
            client.close();
        }

    }

    private static boolean readOkMessage(BufferedReader reader) throws IOException {
        String message;
        while ((message = reader.readLine()) != null) {
            if (message.equalsIgnoreCase(Constants.OK_MESSAGE)) {
                return true;
            }
        }
        return false;
    }

    private static void writeRegisterMessage(PrintWriter writer) {
        JSONObject json = new JSONObject();
        json.put(Constants.MSG_TYPE, Constants.MSG_TYPE_REGISTER);
        writer.println(json.toJSONString());
    }

    private static long readAcknowledgementAndPollingPeriod(BufferedReader reader) throws IOException {
        String message;
        while ((message = reader.readLine()) != null) {
            JSONObject json = (JSONObject) JSONValue.parse(message);
            String msgType = (String) json.get(Constants.MSG_TYPE);
            if (msgType.equals(Constants.MSG_TYPE_ACKNOWLEDGE)) {
                return (Long) json.get(Constants.POLLING_PERIOD);
            }
        }
        throw new IOException("Received unknow message: " + message);
    }
}


