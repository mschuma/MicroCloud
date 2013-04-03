package edu.ncsu.csc.microcloud.daemon;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.Properties;

public class DBHelper {

	public static Connection getConnection(){
		Connection conn = null;
		try{
			Properties properties = PropertiesHelper.getParentProperties();
			Class.forName(properties.getProperty(Constants.DB_DRIVER));
			String uri = Constants.DB_URI;
			String username = properties.getProperty(Constants.DB_USERNAME);
			String password = properties.getProperty(Constants.DB_PASSWORD);
			String host = properties.getProperty(Constants.DB_HOSTNAME);
			String databaseName = properties.getProperty(Constants.DB_NAME);

			uri = uri + host + "/" + databaseName;
			conn = DriverManager.getConnection(uri, username, password);
		}catch(Exception ex){
			System.out.println("Exception while connecting to the database");
			ex.printStackTrace();
		}
		return conn;
	}

	public static void closeConnection(Connection conn){
		try{
			if(conn != null){
				conn.close();
			}
		}catch(Exception ex){
			ex.printStackTrace();
		}
	}

	public static void closeStatement(Statement stmt){
		try{
			if(stmt != null){
				stmt.close();
			}
		}catch(Exception ex){
			ex.printStackTrace();
		}
	}

	public static void closeResultSet(ResultSet rs){
		try{
			if(rs != null){
				rs.close();
			}
		}catch(Exception ex){
			ex.printStackTrace();
		}
	}

}
