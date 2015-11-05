#!/usr/bin/python2.7
__author__ = 'root'
import httplib, urllib
import os
import MySQLdb as mysqldb

MYSQL_HOST = "128.199.106.141"
MYSQL_PASS = "edaA29h7HLCSKrfw"
UFILE = "/home/t/thesis/VM_CUID"
SECRET = "dsgnsbytrynbetumuneubwgvy"

def printText(txt):
    lines = txt.split('\n')
    for line in lines:
        print line.strip()

# get MYSQL connection
def get_mysql_conn():
    try:
        conn = mysqldb.connect(MYSQL_HOST,"root",MYSQL_PASS, "thesis_tor")
        print "Connection to MYSQL Server successful"
        return conn
    except mysqldb.Error, e:
        print e.args[0], e.args[1]
        exit(-1)

conn = get_mysql_conn()


try:
    f = open(UFILE)
    VMID = f.read()

    query = "SELECT port FROM vm_nodes WHERE vmid='"+VMID+"'"

    # deal with mysql
    try:
        cur = conn.cursor()
        cur.execute(query)
        if cur.rowcount > 0:
            res = cur.fetchall()
            PORT = str(res[0][0])
            cmd = '/usr/bin/reverse-ssh -o "ServerAliveInterval 60" -o "ServerAliveCountMax 3" -i /home/t/thesis/ssh_key -N -R '+PORT+':localhost:22 root@128.199.106.141'
            print cmd
            os.system(cmd)
        else:
            print "PORT NOT FOUND for VMID"
    except mysqldb.Error, e:
        print str(e)

except IOError,e:
    print str(e)

