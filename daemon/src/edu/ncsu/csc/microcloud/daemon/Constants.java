package edu.ncsu.csc.microcloud.daemon;

public class Constants {
	
	public static final String MSG_TYPE = "msg_type";
	public static final String MSG_TYPE_REGISTER = "register";
	public static final String MSG_TYPE_UNREGISTER = "unregister";
    public static final String MSG_TYPE_ACKNOWLEDGE = "acknowledge";
	public static final String MSG_IS_ALIVE = "is_alive";


	
	public static final String PARENT_IP = "parent_ip";
	public static final String PARENT_PORT = "parent_port";
	public static final String CHILD_PORT = "child_port";
	public static final String CONNECTION_RETRY_TIME = "connection_retry_time";
	public static final String CONNECTION_RETRIES_ALLOWED = "connection_retries_allowed";
	public static final String POLLING_PERIOD = "polling_period";
	public static final String DB_HOSTNAME = "db_hostname";
	public static final String DB_NAME = "db_name";
	public static final String DB_USERNAME = "db_username";
	public static final String DB_PASSWORD = "db_password";
	public static final String DB_DRIVER = "db_driver";
	public static final String DB_URI = "jdbc:mysql://";
	public static final String DEFAULT_PARENT_IP = "localhost";
	public static final String DEFAULT_PARENT_PORT = "9000";
	public static final String DEFAULT_CHILD_PORT = "9090";
	public static final String DEFAULT_POLLING_PERIOD = "300000";
	public static final String DEFAULT_CONNECTION_RETRIES_ALLOWED = "10";
	public static final String DEFAULT_CONNECTION_RETRY_TIME = "60000";

    public static final String CHILD_SCRIPT_PATH = "child_script_path";
    public static final String PARENT_SCRIPT_PATH = "parent_script_path";
	public static final String DEFAULT_CHILD_SCRIPT_PATH = 
                            "../../../diff-resources/Initial Setup/child.py";
    public static final String DEFAULT_PARENT_SCRIPT_PATH = 
                            "../../../diff-resources/Initial Setup/parent.py";

	public static final String OK_MESSAGE = "OK";
	
	public static final String CHILD_CONFIG_FILE = "child_config.properties";
	public static final String PARENT_CONFIG_FILE = "parent_config.properties";
	
	// TODO: Use keyvalue pair
	public class ChildImage
	{			
		public class Key
		{
			public static final String IMAGE_GROUP_NAME = "child_image_group_name";
			public static final String COMPUTER_GROUP_NAME = "child_computer_group_name";
			public static final String IMAGE_NAME = "child_image_name";
			public static final String IMAGE_PRETTY_NAME = "child_image_prettyname";
			public static final String OWNER_NAME = "owner_name";		
			public static final String DEFAULT_PLATFORM_NAME = "default_platform_name";
			public static final String DEFAULT_PROVISIONING_NAME = "default_provisioning_name";
			public static final String DEFAULT_STATE_NAME = "default_state_name";
			public static final String DEFAULT_SCHEDULE_NAME = "default_schedule_name";
			public static final String DEFAULT_PROC_SPEED = "default_proc_speed";
			public static final String DEFAULT_PROC_NUMBER = "default_proc_number"; 
			public static final String DEFAULT_RAM = "default_RAM";
			public static final String DEFAULT_NETWORK = "default_network";
			public static final String DEFAULT_LOCATION = "default_location";
			public static final String DEFAULT_COMPUTER_TYPE = "default_computer_type"; 
			public static final String DEFAULT_COMPUTER_DRIVE_TYPE = "default_computer_drive_type";			
		}

		public class DefaultValue
		{
			public static final String IMAGE_GROUP_NAME = "LabImage";
			public static final String COMPUTER_GROUP_NAME = "LabComp";
			public static final String IMAGE_NAME = "lab-machine-image1";
			public static final String IMAGE_PRETTYNAME = "Lab machine image";
			public static final String OWNER_NAME = "admin";
			public static final String PLATFORM_NAME = "i386"; 
			public static final String PROVISIONING_NAME = "lab";
			public static final String STATE_NAME = "available";
			public static final String SCHEDULE_NAME = "VCL 24x7";
			public static final String PROC_SPEED = "2000";
			public static final String PROC_NUMBER = "1";
			public static final String RAM = "1024";
			public static final String NETWORK = "1000";			
			public static final String LOCATION = "Lab";
			public static final String COMPUTER_TYPE = "lab";
			public static final String COMPUTER_DRIVE_TYPE = "hda";
		}	 
	}	
}
