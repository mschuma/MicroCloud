#!/usr/bin/env python
import sys, MySQLdb

ip = sys.argv[1]
hostname = sys.argv[2]

host = 'localhost'
user = 'root'
password = ''
database = 'vcl'

conn = MySQLdb.Connection(db=database, host=host, user=user, passwd=password)
mysql = conn.cursor()

#put a check here to see if this IP address entry already exists

insert_query = """ INSERT INTO computer VALUES(null, '2', '1', '1', '1', '8', '8', '8', \
'1024', '2', '2000', '1000', %s, %s, NULL, NULL, \
NULL, 'lab', '3', 'hda', '0', '0000-00-00 00:00:00','Hi' ,NULL, 'Lab',\
NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL) """

mysql.execute(insert_query, (hostname,ip))

find_id_query = "select id from computer where IPaddress=%s; "
mysql.execute(find_id_query, (ip))

id = mysql.fetchall()
comp_id = id[0][0]
print comp_id

#Insert the newly discovered machine into the resource table
insert_resource_query = "insert into resource values(null, '12'," + str(comp_id) +")"
mysql.execute(insert_resource_query)

#find_resourceid_query = "select id from resource where subid=" + str(comp_id) +"and resourcetypeid=12"
find_resourceid_query = "select id from resource where subid=" + str(comp_id)
#find_resourceid_query = "select id from resource where subid=14;"
mysql.execute(find_resourceid_query)

id = mysql.fetchall()
resource_id = id[0][0]
print resource_id

#Insert the newly discovered machine to resourcegroupmember table
insert_resourcegroupmember_query = "insert into resourcegroupmembers values(" + str(resource_id) + ", '12');"
mysql.execute(insert_resourcegroupmember_query)

conn.commit();

print "****Closing mysql****"
mysql.close()
conn.close()