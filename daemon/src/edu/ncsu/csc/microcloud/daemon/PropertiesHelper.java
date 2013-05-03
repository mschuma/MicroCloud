package edu.ncsu.csc.microcloud.daemon;

import java.io.FileReader;
import java.io.IOException;
import java.util.Properties;

/**
 * Provides methods to access the parent and child configuration (.properties)
 * files
 */
public class PropertiesHelper {
	private static final String CLASS_NAME = PropertiesHelper.class
			.getCanonicalName();

	private static Properties parent_properties;
	private static Properties child_properties;

	/**
	 * Retrieves the parent configuration properties
	 * 
	 * @return The parent configuration properties
	 */
	public static Properties getParentProperties() {
		if (parent_properties == null) {
			parent_properties = getProperties(Constants.PARENT_CONFIG_FILE);
		}

		return parent_properties;
	}

	/**
	 * Retrieves the child configuration properties
	 * 
	 * @return The child configuration properties
	 */
	public static Properties getChildProperties() {
		if (child_properties == null) {
			child_properties = getProperties(Constants.CHILD_CONFIG_FILE);
		}

		return child_properties;
	}

	/**
	 * Retrieves the properties from the specified configuration file
	 * 
	 * @param filename
	 *            The name of the configuration file
	 * @return The properties read from the file
	 */
	private static Properties getProperties(String filename) {
		Properties properties = null;
		if (filename != null && !filename.trim().isEmpty()) {
			try {
				properties = new Properties();
				properties.load(new FileReader(filename));

			} catch (IOException ex) {
				System.out
						.println("Exception while loading the property file @ : "
								+ CLASS_NAME);
				ex.printStackTrace();
				System.exit(-1);
			}
		}

		return properties;
	}
}
