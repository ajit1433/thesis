__author__ = 't'
import pyshark
import sys
import os.path
import binascii
import hashlib
from scapy.all import *
import os
import MySQLdb as mysqldb
import string
import subprocess
import json
import numpy
from decimal import*
import csv

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# custom error print
def print_err(txt):
    print bcolors.FAIL + txt + bcolors.ENDC


# get MYSQL connection
def get_mysql_conn():
    try:
        conn = mysqldb.connect("localhost","root","1","thesis_tor")
        print "Connection to MYSQL Server successful"
        return conn
    except mysqldb.Error, e:
        print e.args[0], e.args[1]
        exit(-1)



conn = get_mysql_conn()
cur = conn.cursor()

query = "SELECT id,iperf_output FROM delay_tor_vpn"
cur.execute(query)
rows = cur.fetchall()
i=0
for row in rows:
    #print row[1]
    print "processed: ",i, row[0]
    a = json.loads(row[1])
    #print a
    bw_c2s = a['end']['sum_sent']['bits_per_second']
    bw_s2c = a['end']['sum_received']['bits_per_second']
    query = "UPDATE delay_tor_vpn SET bw_client2server = '" + str(bw_c2s) + "', bw_server2client = '" + str(bw_s2c) + "' WHERE id = '" + str(row[0]) + "'"
    print query
    cur.execute(query)
    conn.commit()
    i += 1

