package edu.ncsu.csc.microcloud.daemon;

import java.sql.Connection;
import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.text.DateFormat;
import java.text.ParseException;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

public class ResourceRegistration {
	
	static class SQLQueries
	{
		public static class Insert
		{
			//		stateid, ownerid, platformid, scheduleid, currentimageid, nextimageid, imagerevisionid, " + 
			//	   "RAM, procnumber, procspeed, network, hostname, IPaddress, privateIPaddress, " + 
			//   	"eth0macaddress, eth1macaddress, type, provisioningid, drivetype, deleted, datedeleted, " +
			//	    "notes, lastcheck, location, dsa, dsapub, rsa, rsapub, host, hostpub, vmhostid, vmtypeid)
			// TODO: When default values are being used do not specify values
			public static final String COMPUTER = "INSERT INTO computer (" +
															   	"stateid, ownerid, platformid, scheduleid, " + 
															   	"currentimageid, nextimageid, imagerevisionid, " + 
														   	    "RAM, procnumber, procspeed, network, " + 
															   	"hostname, IPaddress, privateIPaddress, " + 
															   	"eth0macaddress, eth1macaddress, " + 
															   	"type, provisioningid, " +
															   	"drivetype, " + 
													   			"deleted, datedeleted, " +
														   	    "location) " +
															    "VALUES(" +
														   	    "?, ?, ?, ?, " + 	// stateid, ownerid, platformid, scheduleid (1-4)
														   	    "?, ?, ?, " + 		// currentimageid, nextimageid, imagerevisionid (5-8)
														   	    "?, ?, ?, ?, " + 	// RAM, procnumber, procspeed, network (9-13)
														   	    "?, ?, ?, " + 		// hostname, IPaddress, privateIPaddress (14-16)
														   	    "?, ?, " + 			// eth0macaddress, eth1macaddress (17-18)
														   	    "?, ?, " + 			// type, provisioningid (19-20)
														   	    "?, " + 			// drive type (21)
														   	    // TODO: Unable to parse date time of this format!
														   	    "?, '0000-00-00 00:00:00', " + 			// deleted, datedeleted (22)
														   	    "?)"; 				// location (23)
			
			public static final String RESOURCE = "INSERT INTO resource(resourcetypeid, subid) VALUES(?, ?)";

			public static final String RESOURCE_GROUP_MEMBERS = "INSERT INTO resourcegroupmembers(resourceid, resourcegroupid) VALUES(?, ?)";
		}
		
		public static class Delete
		{
			public static final String COMPUTER = "DELETE FROM computer WHERE IPaddress = ?";

			public static final String RESOURCE = "DELETE FROM resource WHERE id = ?";

			public static final String RESOURCE_GROUP_MEMBERS = "DELETE FROM resourcegroupmembers WHERE resourceid = ? AND resourcegroupid = ?";
		}
		
		public static class SelectId
		{
			public static final String COMPUTER = "SELECT id FROM computer WHERE IPaddress = ?";
			
			public static final String RESOURCE = "SELECT id FROM resource WHERE resourcetypeid = ? AND subid = ?";
			
			public static final String USER = "SELECT id FROM user WHERE lastname = ?";
			
			public static final String SCHEDULE = "SELECT id FROM schedule WHERE name = ?";
			
			public static final String IMAGE = "SELECT id FROM image WHERE name = ?";
				
			public static final String PROVISIONING = "SELECT id FROM provisioning WHERE name = ?";
			
			public static final String PLATFORM = "SELECT id FROM platform WHERE name = ?";	
			
			public static final String STATE = "SELECT id FROM state WHERE name = ?";
			
			public static final String RESOURCE_GROUP = "SELECT id FROM resourcegroup WHERE name = ? AND resourcetypeid = ?";
			
			public static final String RESOURCE_TYPE = "SELECT id FROM resourcetype WHERE name = ?";
		}
		
		// TODO: String name in all CAPS (constant naming convention)
		public static final String SELECT_ALL_IPADDRESSES = "SELECT IPaddress FROM computer";
	}

	public static void registerResource(String resourceIP){
		Connection conn = DBHelper.getConnection();
		Properties properties = PropertiesHelper.getParentProperties();
		
		String imageGroupName = properties.getProperty(Constants.ChildImage.Key.IMAGE_GROUP_NAME, 
				Constants.ChildImage.DefaultValue.IMAGE_GROUP_NAME).trim();
		
		String computerGroupName = properties.getProperty(Constants.ChildImage.Key.COMPUTER_GROUP_NAME, 
				Constants.ChildImage.DefaultValue.COMPUTER_GROUP_NAME).trim();
		
		String ownerName = properties.getProperty(Constants.ChildImage.Key.OWNER_NAME, 
												Constants.ChildImage.DefaultValue.OWNER_NAME).trim();
		
		String imageName = properties.getProperty(Constants.ChildImage.Key.IMAGE_NAME, 
				Constants.ChildImage.DefaultValue.IMAGE_NAME).trim();
		
		String imagePrettyName = properties.getProperty(Constants.ChildImage.Key.IMAGE_PRETTY_NAME, 
				Constants.ChildImage.DefaultValue.IMAGE_PRETTYNAME).trim();
		
		// TODO: Retrieve this information from the child
		String platformName = properties.getProperty(Constants.ChildImage.Key.DEFAULT_PLATFORM_NAME, 
														Constants.ChildImage.DefaultValue.PLATFORM_NAME).trim();
		
		String provisioningName = properties.getProperty(Constants.ChildImage.Key.DEFAULT_PROVISIONING_NAME, 
				Constants.ChildImage.DefaultValue.PROVISIONING_NAME).trim();
		
		String stateName = properties.getProperty(Constants.ChildImage.Key.DEFAULT_STATE_NAME, 
				Constants.ChildImage.DefaultValue.STATE_NAME).trim();
		
		String scheduleName = properties.getProperty(Constants.ChildImage.Key.DEFAULT_SCHEDULE_NAME, 
														Constants.ChildImage.DefaultValue.SCHEDULE_NAME).trim();
		
		Integer procSpeed = Integer.parseInt(properties.getProperty(Constants.ChildImage.Key.DEFAULT_PROC_SPEED, 
				Constants.ChildImage.DefaultValue.PROC_SPEED).trim());
		
		Integer procNumber = Integer.parseInt(properties.getProperty(Constants.ChildImage.Key.DEFAULT_PROC_NUMBER, 
				Constants.ChildImage.DefaultValue.PROC_NUMBER).trim());
		
		Integer ram = Integer.parseInt(properties.getProperty(Constants.ChildImage.Key.DEFAULT_RAM, 
				Constants.ChildImage.DefaultValue.RAM).trim());
		
		Integer networkSpeed = Integer.parseInt(properties.getProperty(Constants.ChildImage.Key.DEFAULT_NETWORK, 
				Constants.ChildImage.DefaultValue.NETWORK).trim());
		
		String computerType = properties.getProperty(Constants.ChildImage.Key.DEFAULT_COMPUTER_TYPE, 
				Constants.ChildImage.DefaultValue.COMPUTER_TYPE).trim();
		
		String computerDriveType = properties.getProperty(Constants.ChildImage.Key.DEFAULT_COMPUTER_DRIVE_TYPE, 
				Constants.ChildImage.DefaultValue.COMPUTER_DRIVE_TYPE).trim();
		
		String location = properties.getProperty(Constants.ChildImage.Key.DEFAULT_LOCATION, 
				Constants.ChildImage.DefaultValue.LOCATION).trim();
		
		try{
			conn.setAutoCommit(false);
			//check if resource is already registered
			int computerId = selectIdFromComputer(conn, resourceIP);
			if(computerId == -1){
				Computer computer = new Computer();
				computer.stateId = selectIdFromTable(conn, SQLQueries.SelectId.STATE, stateName);
				computer.ownerId = selectIdFromTable(conn, SQLQueries.SelectId.USER, ownerName);
				computer.platformId = selectIdFromTable(conn, SQLQueries.SelectId.PLATFORM, platformName);
				computer.scheduleId = selectIdFromTable(conn, SQLQueries.SelectId.SCHEDULE, scheduleName);
				
				Integer imageId = selectIdFromTable(conn, SQLQueries.SelectId.IMAGE, imageName);
				computer.currentImageId = imageId;
				computer.nextImageId = imageId;
				computer.imageRevisionId = imageId;			
				
				computer.RAM = ram;
				computer.procNumber = procNumber;
				computer.procSpeed = procSpeed;
				computer.networkSpeed = networkSpeed;
				
				// TODO: Retrieve from child
				computer.hostName = resourceIP;
				computer.IPAddress = resourceIP;
				computer.privateIPAddress = "";
				computer.eth0MACAddress = "";
				computer.eth1MACAddress = "";
				
				computer.type = computerType;
				computer.provisioningId = selectIdFromTable(conn, SQLQueries.SelectId.PROVISIONING, provisioningName);
				computer.driveType = computerDriveType;

				// TODO: Remove hard coding
				computer.deleted = 0;					
				//computer.dateDeleted = DateFormat.getInstance().parse("0000-00-00 00:00:00");
				
				computer.location = location;
				
				insertIntoComputer(conn, computer);
				computerId = selectIdFromComputer(conn, resourceIP);
				
				int resourceTypeId = selectIdFromTable(conn, SQLQueries.SelectId.RESOURCE_TYPE, "computer");				
				insertIntoResource(conn, resourceTypeId, computerId);				
				
				int resourceId = selectIdFromResource(conn, resourceTypeId, computerId);
				int resourceGroupId = selectIdFromResourceGroup(conn, computerGroupName, resourceTypeId);
						
				insertIntoResourceGroupMembers(conn, resourceId, resourceGroupId);
				conn.commit();
			}else{
				System.out.println("Resource " + resourceIP + " is already registered.");
			}
		}catch(SQLException ex){
			ex.printStackTrace();
			try{
				conn.rollback();
			}catch(SQLException sqlex){
				sqlex.printStackTrace();
			}
//		} catch (ParseException e) {
//			// TODO Auto-generated catch block
//			e.printStackTrace();
		}finally{
			DBHelper.closeConnection(conn);
		}
	}	

	private static int selectIdFromComputer(Connection conn, String ip) throws SQLException{
		PreparedStatement stmt = null;
		ResultSet rs = null;
		int id = -1;
		try{
			stmt = conn.prepareStatement(SQLQueries.SelectId.COMPUTER);
			stmt.setString(1, ip);
			rs = stmt.executeQuery();
			if(rs != null && rs.next()){
				id = rs.getInt("id");
			}
		}finally{
			DBHelper.closeResultSet(rs);
			DBHelper.closeStatement(stmt);
		}
		return id;
	}

	private static int selectIdFromResource(Connection conn, int resourceTypeId, int computerId) throws SQLException{
		PreparedStatement stmt = null;
		ResultSet rs = null;
		int id = -1;
		try{
			stmt = conn.prepareStatement(SQLQueries.SelectId.RESOURCE);
			stmt.setInt(1, resourceTypeId);
			stmt.setInt(2, computerId);
			
			rs = stmt.executeQuery();
			if(rs != null && rs.next()){
				id = rs.getInt("id");
			}
		}finally{
			DBHelper.closeResultSet(rs);
			DBHelper.closeStatement(stmt);
		}
		return id;
	}

	private static int selectIdFromResourceGroup(Connection conn, String name, int resourceTypeId) throws SQLException{
		PreparedStatement stmt = null;
		ResultSet rs = null;
		int id = -1;
		try{
			stmt = conn.prepareStatement(SQLQueries.SelectId.RESOURCE_GROUP);
			stmt.setString(1, name);
			stmt.setInt(2, resourceTypeId);		
			
			rs = stmt.executeQuery();
			if(rs != null && rs.next()){
				id = rs.getInt("id");
			}
		}finally{
			DBHelper.closeResultSet(rs);
			DBHelper.closeStatement(stmt);
		}
		return id;
	}

	private static int selectIdFromTable(Connection conn, String sqlQuery, String whereNameClause) throws SQLException{
		PreparedStatement stmt = null;
		ResultSet rs = null;
		int id = -1;
		try{
			stmt = conn.prepareStatement(sqlQuery);
			stmt.setString(1, whereNameClause);
			rs = stmt.executeQuery();
			if(rs != null && rs.next()){
				id = rs.getInt("id");
			}
		}finally{
			DBHelper.closeResultSet(rs);
			DBHelper.closeStatement(stmt);
		}
		return id;
	}

	private static void insertIntoResourceGroupMembers(Connection conn, int resourceId, int resourceGroupId) throws SQLException{
		PreparedStatement stmt = null;
		try{
			stmt = conn.prepareStatement(SQLQueries.Insert.RESOURCE_GROUP_MEMBERS);
			stmt.setInt(1, resourceId);
			stmt.setInt(2, resourceGroupId);
			stmt.executeUpdate();			
		}finally{
			DBHelper.closeStatement(stmt);
		}

	}

	private static void insertIntoResource(Connection conn, int resourceTypeId, int computerId) throws SQLException{
		PreparedStatement stmt = null;
		try{
			stmt = conn.prepareStatement(SQLQueries.Insert.RESOURCE);
			stmt.setInt(1, resourceTypeId);
			stmt.setInt(2, computerId);
			stmt.executeUpdate();			
		}finally{
			DBHelper.closeStatement(stmt);
		}
	}

	private static void insertIntoComputer(Connection conn, Computer computer) throws SQLException{
		PreparedStatement stmt = null;
		try{
			stmt = conn.prepareStatement(SQLQueries.Insert.COMPUTER);
			stmt.setInt(1, computer.stateId);
			stmt.setInt(2, computer.ownerId);
			stmt.setInt(3, computer.platformId);
			stmt.setInt(4, computer.scheduleId);
			
			stmt.setInt(5, computer.currentImageId);
			stmt.setInt(6, computer.nextImageId);
			stmt.setInt(7, computer.imageRevisionId);
			
			stmt.setInt(8, computer.RAM);
			stmt.setInt(9, computer.procNumber);
			stmt.setInt(10, computer.procSpeed);
			stmt.setInt(11, computer.networkSpeed);
			
			stmt.setString(12, computer.hostName);
			stmt.setString(13, computer.IPAddress);
			stmt.setString(14, computer.privateIPAddress);
			
			stmt.setString(15, computer.eth0MACAddress);
			stmt.setString(16, computer.eth1MACAddress);
			
			stmt.setString(17, computer.type);
			stmt.setInt(18, computer.provisioningId);
			
			stmt.setString(19, computer.driveType);
			
			stmt.setInt(20, computer.deleted);
			//stmt.setDate(20, (java.sql.Date) computer.dateDeleted);
			
			stmt.setString(21, computer.location);		 

			System.out.println(stmt.toString());
			
			stmt.executeUpdate();			
		}
		catch(Exception e)
		{
			e.printStackTrace();
		}
		finally{
			DBHelper.closeStatement(stmt);
		}
	}

	public static void unregisterResource(String resourceIP){
		Connection conn = DBHelper.getConnection();
		Properties properties = PropertiesHelper.getParentProperties();		
		
		String computerGroupName = properties.getProperty(Constants.ChildImage.Key.COMPUTER_GROUP_NAME, 
				Constants.ChildImage.DefaultValue.COMPUTER_GROUP_NAME).trim();
		
		try{
			conn.setAutoCommit(false);
			int computerId = selectIdFromComputer(conn, resourceIP);
			
			int resourceTypeId = selectIdFromTable(conn, SQLQueries.SelectId.RESOURCE_TYPE, "computer");
			int resourceId = selectIdFromResource(conn, resourceTypeId, computerId);
			
			int resourceGroupId = selectIdFromResourceGroup(conn, computerGroupName, resourceTypeId);
			
			deleteFromResourceGroupMembers(conn, resourceId, resourceGroupId);
			deleteFromResource(conn, resourceId);
			deleteFromComputer(conn, resourceIP);
			conn.commit();
		}catch(Exception ex){
			ex.printStackTrace();
			try{
				conn.rollback();
			}catch(SQLException sqlex){
				sqlex.printStackTrace();
			}
		}finally{
			DBHelper.closeConnection(conn);
		}

	}

	private static void deleteFromResourceGroupMembers(Connection conn, int resourceId, int resourceGroupId) throws SQLException{
		System.out.println("Delete entries from ResourceGroupMembers for resource id " + resourceId);
		PreparedStatement stmt = null;
		try{
			stmt = conn.prepareStatement(SQLQueries.Delete.RESOURCE_GROUP_MEMBERS);
			stmt.setInt(1, resourceId);
			stmt.setInt(2, resourceGroupId);
			stmt.executeUpdate();			
		}finally{
			DBHelper.closeStatement(stmt);
		}

	}

	private static void deleteFromResource(Connection conn, int id) throws SQLException{
		System.out.println("Delete  from Resource for resource id " + id);
		PreparedStatement stmt = null;
		try{
			stmt = conn.prepareStatement(SQLQueries.Delete.RESOURCE);
			stmt.setInt(1, id);
			stmt.executeUpdate();			
		}finally{
			DBHelper.closeStatement(stmt);
		}

	}

	private static void deleteFromComputer(Connection conn, String resourceIP) throws SQLException{
		System.out.println("Delete  from Computer for ip " + resourceIP);
		PreparedStatement stmt = null;
		try{
			stmt = conn.prepareStatement(SQLQueries.Delete.COMPUTER);
			stmt.setString(1, resourceIP);			
			stmt.executeUpdate();			
		}finally{
			DBHelper.closeStatement(stmt);
		}
	}

	public static List<String> getChildren(Connection conn){
		List<String> children = null;
		PreparedStatement stmt = null;
		ResultSet rs = null;
		if(conn != null){
			children = new ArrayList<String>();
			try{
				stmt = conn.prepareStatement(SQLQueries.SELECT_ALL_IPADDRESSES);				
				rs = stmt.executeQuery();
				while(rs.next()){
					children.add(rs.getString(1));
				}
			}catch(SQLException sqlex){
				sqlex.printStackTrace();
			}finally{
				DBHelper.closeStatement(stmt);
				DBHelper.closeResultSet(rs);
			}
		}
		return children;
	}

}
