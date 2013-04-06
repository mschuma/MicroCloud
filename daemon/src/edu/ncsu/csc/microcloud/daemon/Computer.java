package edu.ncsu.csc.microcloud.daemon;

import java.util.Date;

public class Computer
{
	// TODO: Create accessors
	public Integer stateId;
 	public Integer ownerId; 	
 	public Integer platformId;
 	public Integer scheduleId;
 	public Integer currentImageId;
 	public Integer nextImageId;
 	public Integer imageRevisionId;
 	public Integer RAM; 
 	public Integer procNumber;
 	public Integer procSpeed;
 	public Integer networkSpeed;
 	public String hostName;
 	public String IPAddress;
 	public String privateIPAddress;
 	public String eth0MACAddress;
 	public String eth1MACAddress;
 	public Integer provisioningId;
 	public String type;
 	public String driveType;
 	// TODO: Enumeration
 	public Integer deleted;
 	public Date dateDeleted;
 	public String location;	 	
}