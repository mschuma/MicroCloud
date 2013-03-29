package edu.ncsu.csc.microcloud.daemon;


public class Constants {
	
	public static final String MSG_TYPE = "msg_type";
	public static final String MSG_TYPE_REGISTER = "register";
	public static final String MSG_TYPE_UNREGISTER = "unregister";
	public static final String MSG_IS_ALIVE = "is_alive";
	
	public static final String PARENT_IP = "parent_ip";
	public static final String PARENT_PORT = "parent_port";
	public static final String CHILD_PORT = "child_port";
	public static final String POLLING_PERIOD = "polling_period";
	public static final String DEFAULT_PARENT_IP = "localhost";
	public static final String DEFAULT_PARENT_PORT = "9000";
	public static final String DEFAULT_CHILD_PORT = "9090";
	public static final String DEFAULT_POLLING_PERIOD = "300000";
	
	public static final String OK_MESSAGE = "OK";
	
	public static final String CONFIG_FILE = "config.properties";
}
