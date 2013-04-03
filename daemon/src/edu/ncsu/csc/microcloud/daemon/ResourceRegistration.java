package edu.ncsu.csc.microcloud.daemon;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class ResourceRegistration {
	private static final String insert_into_computer = "INSERT INTO computer VALUES(null, 2, 1, 1, 1, 8, 8, 8," +
			"1024, 2, 2000, 1000, ? , ?, NULL, NULL," + 
			"NULL, 'lab', 3, 'hda', 0, 'Note', '0000-00-00 00:00:00', NULL, 'Lab'," +
			"NULL, NULL, NULL, NULL, NULL, NULL, NULL)";

	private static final String insert_into_resource = "insert into resource values(null, 12, ?)";

	private static final String insert_into_resourcegroupmembers = "insert into resourcegroupmembers values(?, 12)";

	private static final String delete_from_computer = "delete from computer where IPaddress = ?";

	private static final String delete_from_resource = "delete from resource where id = ?";

	private static final String delete_from_resourcegroupmembers = "delete from resourcegroupmembers where resourceid = ?";

	private static final String select_id_from_computer = "select id from computer where IPaddress = ?";

	private static final String select_id_from_resource = "select id from resource where subid = ?";

	public static void registerResource(String resourceIP){
		Connection conn = DBHelper.getConnection();

		try{
			conn.setAutoCommit(false);
			//check if resource is already registered
			int computerId = selectIdFromComputer(conn, resourceIP);
			if(computerId == -1){
				insertIntoComputer(conn, resourceIP);
				computerId = selectIdFromComputer(conn, resourceIP);
				insertIntoResource(conn, computerId);
				int resourceId = selectIdFromResource(conn, computerId);
				insertIntoResourceGroupMembers(conn, resourceId);
				conn.commit();
			}else{
				System.out.println("Resource " + resourceIP + " is already registered.");
			}
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

	private static int selectIdFromComputer(Connection conn, String ip) throws SQLException{
		PreparedStatement stmt = null;
		ResultSet rs = null;
		int id = -1;
		try{
			stmt = conn.prepareStatement(select_id_from_computer);
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

	private static int selectIdFromResource(Connection conn, int computerId) throws SQLException{
		PreparedStatement stmt = null;
		ResultSet rs = null;
		int id = -1;
		try{
			stmt = conn.prepareStatement(select_id_from_resource);
			stmt.setInt(1, computerId);
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

	private static void insertIntoResourceGroupMembers(Connection conn, int resourceId) throws SQLException{
		PreparedStatement stmt = null;
		try{
			stmt = conn.prepareStatement(insert_into_resourcegroupmembers);
			stmt.setInt(1, resourceId);
			stmt.executeUpdate();			
		}finally{
			DBHelper.closeStatement(stmt);
		}

	}

	private static void insertIntoResource(Connection conn, int id) throws SQLException{
		PreparedStatement stmt = null;
		try{
			stmt = conn.prepareStatement(insert_into_resource);
			stmt.setInt(1, id);
			stmt.executeUpdate();			
		}finally{
			DBHelper.closeStatement(stmt);
		}

	}

	private static void insertIntoComputer(Connection conn, String resourceIP) throws SQLException{
		PreparedStatement stmt = null;
		try{
			stmt = conn.prepareStatement(insert_into_computer);
			stmt.setString(1, resourceIP);
			stmt.setString(2, resourceIP);
			stmt.executeUpdate();			
		}finally{
			DBHelper.closeStatement(stmt);
		}

	}

	public static void unregisterResource(String resourceIP){
		Connection conn = DBHelper.getConnection();
		try{
			conn.setAutoCommit(false);
			int computerId = selectIdFromComputer(conn, resourceIP);			
			int resourceId = selectIdFromResource(conn, computerId);			
			deleteFromResourceGroupMembers(conn, resourceId);
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

	private static void deleteFromResourceGroupMembers(Connection conn, int resourceId) throws SQLException{
		System.out.println("Delete entries from ResourceGroupMembers for resource id " + resourceId);
		PreparedStatement stmt = null;
		try{
			stmt = conn.prepareStatement(delete_from_resourcegroupmembers);
			stmt.setInt(1, resourceId);
			stmt.executeUpdate();			
		}finally{
			DBHelper.closeStatement(stmt);
		}

	}

	private static void deleteFromResource(Connection conn, int id) throws SQLException{
		System.out.println("Delete  from Resource for resource id " + id);
		PreparedStatement stmt = null;
		try{
			stmt = conn.prepareStatement(delete_from_resource);
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
			stmt = conn.prepareStatement(delete_from_computer);
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
				stmt = conn.prepareStatement("select IPaddress from computer");				
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
