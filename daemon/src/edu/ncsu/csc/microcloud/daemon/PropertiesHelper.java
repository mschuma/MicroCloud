package edu.ncsu.csc.microcloud.daemon;

import java.io.FileReader;
import java.io.IOException;
import java.util.Properties;

public class PropertiesHelper {
	private static final String CLASS_NAME = PropertiesHelper.class.getCanonicalName();
	private static Properties parent_properties;
	private static Properties child_properties;	

	public static Properties getParentProperties(){
		if(parent_properties == null){
			parent_properties = getProperties(Constants.PARENT_CONFIG_FILE);
		}
		return parent_properties;
	}

	public static Properties getChildProperties(){
		if(child_properties == null){
			child_properties = getProperties(Constants.CHILD_CONFIG_FILE);
		}
		return child_properties;
	}

	public static Properties getProperties(String filename){
		Properties properties = null;
		if(filename != null && !("".equals(filename.trim()))){
			try{
				properties = new Properties();			
				properties.load(new FileReader(filename));		

			}catch(IOException  ex){
				System.out.println("Exception while loading the property file @ : " + CLASS_NAME);
				ex.printStackTrace();
				System.exit(-1);
			}
		}
		return properties;
	}

}
