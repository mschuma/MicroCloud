#!/usr/bin/env python
import sys, MySQLdb

ip = sys.argv[1]

host = 'localhost'
user = 'root'
password = ''
database = 'vcl'

conn = MySQLdb.Connection(db=database, host=host, user=user, passwd=password)
mysql = conn.cursor()

find_id_query = "select id from computer where IPaddress=%s; "
mysql.execute(find_id_query, (ip))

id = mysql.fetchall()

# add check if ipaddress is not present in table

comp_id = id[0][0]
print comp_id

find_resourceid_query = "select id from resource where subid=" + str(comp_id) +" and resourcetypeid=12"
mysql.execute(find_resourceid_query)

id = mysql.fetchall()
resource_id = id[0][0]
print resource_id

# Delete the entry for this machine from computer table
delete_id_query = "delete from computer where id=" + str(comp_id)
mysql.execute(delete_id_query)

#Delete the entry for this machine from resource table
delete_resourceid_query = "delete from resource where id=" + str(resource_id)
mysql.execute(delete_resourceid_query)

#Delete the entry for this machine from resourcegroupmember table
delete_resourcegroupmember_query = "delete from resourcegroupmembers where resourceid=" + str(resource_id) + " and resourcegroupid=12"
mysql.execute(delete_resourcegroupmember_query)

conn.commit();

print "****Closing mysql****"
mysql.close()
conn.close()