package edu.ncsu.csc.microcloud.daemon;

import java.io.IOException;
import java.util.Properties;

public class PropertiesHelper {
	private static final String CLASS_NAME = PropertiesHelper.class.getCanonicalName();
	private static Properties properties;
	
	static{
		try{
			properties = new Properties();			
			properties.load(Properties.class.getResourceAsStream("/" + Constants.CONFIG_FILE));
		}catch(IOException  ex){
			System.out.println("Exception while loading the property file @ : " + CLASS_NAME);
			ex.printStackTrace();
		}
	}
	
	public static Properties getProperties(){
		return properties;
	}

}
