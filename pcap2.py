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
FIRST_RUN = True
LOCAL_DIR = "/home/t/thesis/processing/thesis-master/"
REMOTE_DIR = "/home/t/thesis/processing/remote-pcap/"

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
query = "SELECT id,call_id from delay_tor_vpn WHERE dirty = 0"
cur.execute(query)
rows = cur.fetchall()

query = ""
k = 0
for row in rows:
    print k, "Processing Call", row[1]

    pcap_local = row[1] + ".pcap"
    pcap_remote = "remote_" + row[1] + ".pcap"
    wav = row[1] + ".wav"

    query = "INSERT INTO delay_tor_vpn_details SET call_id = '" + row[1] + "', "

    if FIRST_RUN:
        cmd = "tshark -r " + LOCAL_DIR + pcap_local + " -w " + LOCAL_DIR + "new_" + pcap_local + " -F libpcap"
        #print cmd
        os.system(cmd)
        cmd = "tshark -r " + REMOTE_DIR + pcap_remote + " -w " + REMOTE_DIR + "new_" + pcap_remote + " -F libpcap"
        #print cmd
        os.system(cmd)

    pcapf_local = PcapReader(LOCAL_DIR + "new_" + pcap_local)
    pcapf_remote = PcapReader(REMOTE_DIR + "new_" + pcap_remote)


    pcap_local_hash = []
    pcap_remote_hash = []
    pcap_local_time = []
    pcap_remote_time = []

    for p1 in pcapf_local:
        a = hashlib.sha1(binascii.hexlify(str(p1)))
        pcap_local_hash.append(a.hexdigest())
        pcap_local_time.append(p1.time)

    for p2 in pcapf_remote:
        a = hashlib.sha1(binascii.hexlify(str(p2)))
        pcap_remote_hash.append(a.hexdigest())
        pcap_remote_time.append(p2.time)

    i=0
    count = 0
    packet_delay = []

    for p1 in pcap_remote_hash:
        j=0
        for p2 in pcap_local_hash:
            if p1==p2:
                #packet_order_str += str(i) + ":" + str(j) + ","
                packet_delay.append(numpy.absolute(pcap_local_time[j]-pcap_remote_time[i]))
                break
            j+=1
            count+=1
        i+=1
    query += "delay_string ='" + mysqldb.escape_string(json.dumps(packet_delay)) + "', "
    query += "delay_mean = '" + str(numpy.mean(packet_delay)) + "', "
    query += "delay_median = '" + str(numpy.median(packet_delay)) + "', "
    query += "delay_avg ='" + str(numpy.average(packet_delay)) + "', "
    query += "delay_min = '" + str(numpy.min(packet_delay)) + "', "
    query += "delay_max = '" + str(numpy.max(packet_delay)) + "', "
    query += "delay_sd = '" + str(numpy.std(packet_delay)) + "', "
    query += "delay_var = '" + str(numpy.var(packet_delay)) + "', "

    # compute jitter
    prev = 0
    packet_jitter = []
    for i in packet_delay:
        packet_jitter.append(numpy.absolute(i - prev))
        prev = i

    query += "jitter_string = '" + mysqldb.escape_string(json.dumps(packet_jitter)) + "', "
    query += "jitter_mean = '" + str(numpy.mean(packet_jitter)) + "', "
    query += "jitter_median = '" + str(numpy.median(packet_jitter)) + "', "
    query += "jitter_avg ='" + str(numpy.average(packet_jitter)) + "', "
    query += "jitter_min = '" + str(numpy.min(packet_jitter)) + "', "
    query += "jitter_max = '" + str(numpy.max(packet_jitter)) + "', "
    query += "jitter_sd = '" + str(numpy.std(packet_jitter)) + "', "
    query += "jitter_var = '" + str(numpy.var(packet_jitter)) + "',"

    # print query
    query = string.rstrip(query,",")
    #print query
    k += 1
    try:
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        print bcolors.BOLD + "Record inserted into database..." + bcolors.ENDC
    except:
        print_err("Error in inserting data to DB...")


exit(0)