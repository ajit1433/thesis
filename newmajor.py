__author__ = 'anonymous'

from stem.control import Controller
from stem import Signal
import stem.socket as Socket
import stem
import os
import sys
import time
import MySQLdb as mysqldb
import pexpect
import multiprocessing
import subprocess
import shutil
import pxssh
import string
from uniqueVMIdGen import *
import commands

# constants
MAX_CALL = 800
REMOTE_HOST = "10.8.0.1"
REMOTE_HOST_NO_VPN = "128.199.106.141"
REMOTE_USER = "root"
REMOTE_HOST_IPERF_PORT = 2222
TOR_PASSWORD= str(1)
WORKING_DIR = os.getcwd()
REMOTE_HOST_SSH_KEY = WORKING_DIR+"/ssh_key"
VMID = ""
global OR1_ID
global OR2_ID
global OR3_ID

OR1_ID = 0
OR2_ID = 0
OR3_ID = 0


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# check root
def check_root():
    if os.geteuid()!=0:
        print >> sys.stdin, "You need root permissions to run this. See ya"
        exit(-1)


# Installing IPTable rules..."
def install_iptables():
    print "Installing IPTable rules"
    cmd = WORKING_DIR+"/./anonlocal1.sh"
    os.system(cmd)
    print "Done installing IPTable rules..."


# get MYSQL connection
def get_mysql_conn():
    try:
        conn = mysqldb.connect("localhost","root","1","thesis_tor")
        print "Connection to MYSQL Server successful"
        return conn
    except mysqldb.Error, e:
        print e.args[0], e.args[1]
        exit(-1)


def get_routers(conn, id1, id2, id3):
    or1 = None
    or2 = None
    or3 = None
    cur = conn.cursor()

    # get guard or
    query = "SELECT id, hash, router_name FROM tor_nodes WHERE guard_server = '1' and id > '"+str(id1)+"' LIMIT 1"
    # print bcolors.OKGREEN + query + bcolors.ENDC
    try:
        cur.execute(query)
        for row in cur.fetchall():
            or1 = row
    except:
        print "Error in getting guard-server"
        exit(-1)

    # get guard or
    query = "SELECT id, hash, router_name FROM tor_nodes WHERE id != '"+str(id1)+"' and id > '"+str(id2)+"' LIMIT 1"
    # print bcolors.OKGREEN + query + bcolors.ENDC
    try:
        cur.execute(query)
        for row in cur.fetchall():
            or2 = row
    except:
        print "Error in getting middle-server"
        exit(-1)

    # get guard or
    query = "SELECT id, hash, router_name FROM tor_nodes WHERE exit_server = '1' and id > '"+str(id3)+"' and id != '"+str(id1)+"' and id != '"+str(id1)+"' LIMIT 1"
    # print_err bcolors.OKGREEN + query + bcolors.ENDC
    try:
        cur.execute(query)
        for row in cur.fetchall():
            or3 = row
    except:
        print "Error in getting guard-server"
        exit(-1)

    return [or1, or2, or3]


# custom error print
def print_err(txt):
    print bcolors.FAIL + txt + bcolors.ENDC


# dump packet local
def dump_packets(name_pkt_dump_file):
    os.chdir("/root")
    subprocess.Popen(["tshark", "-i", "tun0", "-w", name_pkt_dump_file])


# attach stream to circuit
def attach_stream(stream):
    if stream.status == 'NEW':
        try:
            controller.attach_stream(stream.id, circuit_id)
        except stem.UnsatisfiableRequest, e:
            print_err("Error in attaching stream: "+str(e))

# get vmid from uniqueVMIdGen.py
get_vmid()
f = open(UFILE,"r+")
VMID = f.readline()
f.close()
print VMID

# make folder for vmid on sevrer
cmd = "ssh -i " + REMOTE_HOST_SSH_KEY + " " + REMOTE_USER + "@" + REMOTE_HOST_NO_VPN + " mkdir " + VMID + " &"
print cmd
os.system(cmd)
print "folder for VM created at Server."

check_root()
install_iptables()
conn = get_mysql_conn()

with Controller.from_port(port=9051) as controller:
    controller.authenticate(TOR_PASSWORD)

    # prepare for custom connection
    controller.reset_conf()
    controller.set_conf("__DisablePredictedCircuits", "1")
    controller.set_conf("MaxOnionsPending", "0")
    controller.set_conf("newcircuitperiod", "999999999")
    controller.set_conf("maxcircuitdirtiness", "999999999")
    controller.set_conf("__LeaveStreamsUnattached", "1")      # leave stream management to programmer
    print "Preparation for custom circuit completed"

    # change to master directory
    if not os.path.isdir("thesis-master"):
        os.mkdir("thesis-master")
    os.chdir("thesis-master")

    # file store path
    storage_path = os.getcwd()

    call = 0
    count = 0
    while call < MAX_CALL:

        FLAG_DIRTY_REMOTE_TIME_SYNC = False
        FLAG_DIRTY = False

        # get timestamp for file name
        localtime = str(time.time())
        name_sound_file = localtime + ".wav"
        name_pkt_dump_file = localtime + ".pcap"

        query = "INSERT INTO delay_tor_vpn SET call_id = '" + localtime + "',"

        # close all existing circuit
        c = controller.get_circuits()
        for cn in c:
            controller.close_circuit(cn.id)
        print "All existing circuits closed..."

        # get circuit
        try:
            # get or1, or2, or3 from table
            id = get_routers(conn, OR1_ID, OR2_ID, OR3_ID)
            try:
                OR1_ID = id[0][0]
                OR2_ID = id[1][0]
                OR3_ID = id[2][0]
                query = query + " or1_hash = '" + id[0][1] + "', or1_name = '" + id[0][2] + "', or2_hash = '" + id[1][1] + "', or2_name = '" + id[1][2] + "', or3_hash = '" + id[2][1] + "', or3_name = '" + id[2][2] + "',"
            except TypeError, e:
                txt = "Error in getting ORs"+str(e)
                print_err(txt)
                exit(-1)

            # build circuit
            circuit_id = controller.new_circuit(path=[id[0][1], id[1][1], id[2][1]], await_build=True)
            count += 1
            print bcolors.HEADER, count, "Circuit build successful",id[0][0], id[1][0], id[2][0], id[0][2], id[1][2], id[2][2] + bcolors.ENDC

            # attach all streams to this circuit
            controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

            # create vpn
            try:
                vpn_process = pexpect.spawn('openvpn --config ' + WORKING_DIR + '/client.ovpn', timeout=180)
                vpn_process.expect('Initialization Sequence Completed', timeout=-1)
                print "VPN Connection established..."
            except pexpect.ExceptionPexpect, e:
                # print bcolors.WARNING + "ExceptionPexpect in establishing VPN",e, bcolors.ENDC
                txt = "ExceptionPexpect in establishing VPN"+str(e)
                print_err(txt)
                continue

            # do your thing
            # os.system("ping 10.8.0.1 -c 10")

            # bandwidth measuring
            print "iperf3 Bandwidth calculation started"
            cmd = "iperf3 -c " + REMOTE_HOST + " -p " + str(REMOTE_HOST_IPERF_PORT)+ " -J -i 10 -f K -4 > iperfout.txt"
            os.system(cmd)
            with open('iperfout.txt', 'a+') as fq:
                a = fq.read()
                query = query + " iperf_output='" + mysqldb.escape_string(a) + "',"

            # do time syncornization at remote end
            print "started time sycnronization..."
            cmd = "ssh -i " + REMOTE_HOST_SSH_KEY + " " + REMOTE_USER + "@" + REMOTE_HOST + " ntpdate 1.ubuntu.pool.ntp.org &"
            os.system(cmd)
            time.sleep(5)
            print "remote time sycnronization done"

            # time syncronization at local machine
            os.system("sudo ntpdate 1.ubuntu.pool.ntp.org")
            print "local time sycnronization done"

            try:
                # setup packet dump remote
                cmd = "ssh -i " + REMOTE_HOST_SSH_KEY + " " + REMOTE_USER + "@" + REMOTE_HOST + " tshark -i tun0 -f \\'port not " + str(REMOTE_HOST_IPERF_PORT) + " and port not 22\\' -w " + VMID + "/remote_" + name_pkt_dump_file + " &"
                os.system(cmd)
                time.sleep(5)
                print "Remote pcap started..."

                # setup packetdump: tshark local
                tshark_process = multiprocessing.Process(target=dump_packets, args=(name_pkt_dump_file,))
                tshark_process.start()
                print "Local pcap started..."

                                
                # kill process if its not ended
                process_cmd = commands.getstatusoutput("netstat -nlp | grep 5080 | awk '{print $7}'")
                a = process_cmd[1]
                process_id = a[0:a.find("/")]
                os.system("kill -9 " + process_id)

                process_cmd = commands.getstatusoutput("netstat -nlp | grep 5080 | awk '{print $6}'")
                a = process_cmd[1]
                process_id = a[0:a.find("/")]
                os.system("kill -9 " + process_id)
                time.sleep(1)      
                
                # make call
                cmd = "python " + WORKING_DIR + "/record-sample.py " + name_sound_file
                call_record_process = pexpect.spawn(cmd, timeout=600)

                # make 1 call, record it and end
                call_record_process.expect('pjsua_core.c  .PJSUA destroyed')
                print "Recording done."

                # stop packet dump and move packet dump file to appropriate folder
                cmd = "ssh -i " + REMOTE_HOST_SSH_KEY + " " + REMOTE_USER + "@" + REMOTE_HOST + " killall tshark"
                os.system(cmd)
                print "Remote tshark stopped"

                os.system("sudo killall tshark")
                print "Local tshark stopped"
                src_path_file = "/root/" + name_pkt_dump_file
                dst_path_file = storage_path + "/" + name_pkt_dump_file
                errors = []
                try:
                    shutil.move(src_path_file, dst_path_file)
                except IOError, e:
                    print_err(str(e))
                    query += " dirty = '1',"

            except pexpect.ExceptionPexpect, e:
                print_err(str(e))

            # close vpn
            vpn_process.send('\003')
            vpn_process.expect("process exiting")
            print "VPN Process exited..."

            query += " vmid = '"+ VMID +"',"
            query = (string.rstrip(query, ","))
            # deal with mysql
            try:
                cur = conn.cursor()
                cur.execute(query)
                conn.commit()
                print bcolors.BOLD + "Record inserted into database..." + bcolors.ENDC
            except:
                print_err("Error in inserting data to DB...")

            query += "\r\n"
            with open("query_file.txt","a+") as fp:
                fp.write(query)

        except stem.ControllerError, e:
            # print bcolors.FAIL, e, bcolors.ENDC
            print_err(str(e))
        finally:
            controller.remove_event_listener(attach_stream)

        call += 1
