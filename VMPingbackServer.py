#!/usr/bin/python2.7
import httplib, urllib
import os
import MySQLdb as mysqldb

MYSQL_HOST = "localhost" #"128.199.106.141"
MYSQL_PASS = "1" #"edaA29h7HLCSKrfw"
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


def pingback():
    httpServ = httplib.HTTPConnection("128.199.106.141", 80)
    httpServ.connect()

    params = {"error":"0", "vmid":"0","call_count":"0", "dat":"dsgnsbytrynbetumuneubwgvy"}

    if os.path.exists(UFILE):

        try:
            f = open(UFILE)
            VMID = f.read()
            params['vmid'] = VMID
        except IOError,e:
            params['error'] = str(e)

    else:
        params['error'] = "vmid not found at path"


    conn = get_mysql_conn()
    query = "SELECT count(id) FROM delay_tor_vpn"
    # deal with mysql
    try:
        cur = conn.cursor()
        cur.execute(query)
        res = cur.fetchall()
        params["call_count"] = str(res[0][0])
    except mysqldb.Error, e:
        params["error"] += "Error in inserting data to DB..." + str(e)


    httpServ.request('GET', '/pingback.php?'+urllib.urlencode(params))

    response = httpServ.getresponse()
    if response.status == httplib.OK:
        print "Output from CGI request"
        printText (response.read())
    httpServ.close()

if __name__ == "__main__":
    pingback()
