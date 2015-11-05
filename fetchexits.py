#!/usr/bin/python

import urllib2
import sys
import string
import _mysql as mysql
from bs4 import BeautifulSoup


class tor_node:
    router_lat = ""  # latitude
    router_long = ""  # longitude
    router_country = ""  # country
    router_name = ""  # string
    hash = ""  # string
    bandwidth = 0  # KB/s, integer
    uptime = ""  # string "x" d
    hostname = ""  # string
    fast_server = 0  # 0/1
    exit_server = 0  # 0/1
    directory_server = 0  # 0/1
    guard_server = 0  # 0/1
    stable_server = 0  # 0/1
    authority_server = 0  # 0/1
    os = ""  # operating server
    version = ""  # string
    running = 0  # 0/1
    hibernating = 0  # 0/1
    valid = 0  # 0/1
    V2Dir = 0  # 0/1
    bw_max = 0  # max bandwidth
    bw_burst = 0  # burst bandwidth
    bw_observed = 0  # observed bw
    descriptor_publish_date = ""  # DATE
    family = ""  # string
    ORPort = ""  # integer / string:none
    DirPort = ""  # integer / string:none
    bad_exit = 0  # 0/1
    bad_directory = 0  # 0/1
    exit_policy = ""  # multi-line string
    ip = ""  # string

    def __init__(self, router_lat="", router_long="", router_country="", router_name="", hash="", bandwidth=0,
                 uptime="", \
                 hostname="", fast_server=0, exit_server=0, directory_server=0, \
                 guard_server=0, stable_server=0, authority_server=0, os="", version="", runnning=0, hibernating=0, \
                 valid=0, V2Dir=0, bw_max=0, bw_burst=0, bw_observed=0, descriptor_publish_date="", \
                 family="", ORPort="", DirPort="", bad_exit=0, bad_directory=0, exit_policy="", ip=""):
        # print "initiliaing"
        self.router_lat = router_lat
        self.router_long = router_long
        self.router_country = router_country
        self.router_name = router_name
        self.hash = hash
        self.bandwidth = bandwidth
        self.uptime = uptime
        self.hostname = hostname
        self.fast_server = fast_server
        self.exit_server = exit_server
        self.directory_server = directory_server
        self.guard_server = guard_server
        self.stable_server = stable_server
        self.authority_server = authority_server
        self.os = os
        self.version = version
        self.running = runnning
        self.hibernating = hibernating
        self.valid = valid
        self.V2Dir = V2Dir
        self.bw_max = bw_max
        self.bw_burst = bw_burst
        self.bw_observed = bw_observed
        self.descriptor_publish_date = descriptor_publish_date
        self.family = family
        self.ORPort = ORPort
        self.DirPort = DirPort
        self.bad_exit = bad_exit
        self.bad_directory = bad_directory
        self.exit_policy = exit_policy
        self.ip = ip


def fetch():
    # Just a quick note: I feel there's no reason to blanket ban relay nodes.
    # A person runs a relay node as opposed to an exit to avoid the backlash
    # normally associated with running an exit. Relay operators shouldn't be
    # be punished for doing literally the least they can do to help out.
    #
    # I'm not against Tor, but it's just not "for" certain things, due to abuse.
    #
    # So, long story short, this only returns exits.
    # Also, it doesn't take exit policies into account.
    # It's a little hamhanded, but it's dead simple to implement.

    try:
        conn = mysql.connect("localhost", "root", "1", "thesis_tor")
        # query = """insert into tor_nodes (router_lat,router_long, router_country, hash, router_name, bandwidth, uptime, hostname, ip, fast_server, exit_server, directory_server, guard_server, stable_server, authority_server, os, version, ORPort, DirPort, bad_exit) values (%s, %s, %s, %s, %s, %d, %s, %s, %s, %d, %d, %d, %d, %d, %d, %s, %s, %s, %s, %d)"""
        # query = """insert into tor_nodes (router_lat,router_long, router_country, hash, router_name,
        #    bandwidth, uptime, hostname, ip, fast_server, exit_server, directory_server, guard_server,
        #    stable_server, authority_server, os, version, ORPort, DirPort, bad_exit) values
        #    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        # query += ", ["
    except mysql.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)

    nodes_list = []
    i = 0

    for line in urllib2.urlopen('http://torstatus.blutmagie.de/'):
        # print line
        if "router_detail.php?FP" in line:
            temp = tor_node()
            # tquery = '('

            # get lat
            start = string.find(line, "openstreetmap.org/?mlon=") + 24
            end = string.find(line, "&mlat", start)
            if start >= 24:
                # print line[start:end],start,(end-start)
                temp.router_lat = line[start:end]
                line = line[end:]  # line truncated
            # tquery = tquery + '"' + temp.router_lat + '"' + ', '

            # get long
            start = string.find(line, "&mlat=") + 6
            end = string.find(line, "&zoom=", start)
            if start >= 6:
                # print line[start:end],start,(end-start)
                temp.router_long = line[start:end]
                line = line[end:]  # line truncated
            # tquery = tquery + '"' + temp.router_long + '"' + ', '

            # get country
            start = string.find(line, "alt='") + 5
            if start >= 5:
                end = string.find(line, "' border='", start)
                # print line[start:end],start,(end-start)
                temp.router_country = line[start:end]
                line = line[end:]  # line truncated
            print temp.router_country

            # get hash
            start = string.find(line, "router_detail.php?FP=") + 21
            end = string.find(line, "' target='", start)
            if start >= 21:
                # print line[start:end],start,(end-start)
                temp.hash = line[start:end]
                line = line[end:]  # line truncated
            # tquery = tquery + '"' + temp.hash + '"' + ', '

            # get router name
            start = string.find(line, "' target='_blank'>") + 18
            end = string.find(line, "</a></td>", start)
            if start >= 18:
                # print line[start:end],start,(end-start)
                temp.router_name = line[start:end]
                line = line[end:]  # line truncated
            # tquery = tquery + '"' + temp.router_name + '"' + ', '

            # get bandwidth
            start = string.find(line, "class='bwb'><tr title='") + 23
            end = string.find(line, " KBs'><td", start)
            if start >= 23:
                temp.bandwidth = line[start:end]
                line = line[end:]  # line truncated
            # tquery = tquery + str(temp.bandwidth) + ', '

            # get uptime
            start = string.find(line, "</td><td class='TDcb'><b>") + 25
            if start >= 26:
                end = string.find(line, "</b></td><td class='TDS'>", start)
                temp.uptime = line[start:end]
                line = line[end:]  # line truncated
            else:
                start = string.find(line, "</td><td class='TDcb'>") + 22
                end = string.find(line, "</td><td class='TDS'>", start)
                if start >= 23:
                    temp.uptime = line[start:end]

                    line = line[end:]  # line truncated
            # tquery = tquery + '"' + temp.uptime + '"' + ', '
            # print temp.uptime

            # get hostname
            start = string.find(line, "'><tr><td class='iT'>") + 21
            end = string.find(line, "[<a class='who'", start)
            if start >= 21:
                temp.hostname = line[start:end]
                line = line[end:]  # line truncated
            # tquery = tquery + '"' + temp.hostname + '"' + ', '

            # get IP
            start = string.find(line, "='/cgi-bin/whois.pl?ip=") + 23
            end = string.find(line, "' target='_blank'>", start)
            if start >= 23:
                temp.ip = line[start:end]
                line = line[end:]  # line truncated
            # tquery = tquery + '"' + temp.ip + '"' + ', '

            # get Fast Server
            x = string.find(line, "alt='Fast Server'") + 17
            if x >= 17:
                temp.fast_server = 1
                line = line[start + 17:]  # line truncated
            # tquery = tquery + str(temp.fast_server) + ', '

            # get Exit Server
            x = string.find(line, "alt='Exit Server'") + 17
            if x >= 17:
                temp.exit_server = 1
                line = line[start + 17:]  # line truncated
            # tquery = tquery + str(temp.exit_server) + ', '

            # get Directory Server
            x = string.find(line, "alt='Directory Server'") + 22
            if x >= 22:
                temp.directory_server = 1
                line = line[start + 22:]  # line truncated
            # tquery = tquery + str(temp.directory_server) + ', '

            # get Guard Server
            x = string.find(line, "alt='Guard Server'") + 18
            if x >= 18:
                temp.guard_server = 1
                line = line[start + 18:]  # line truncated
            # tquery = tquery + str(temp.guard_server) + ', '

            # get stable Server
            x = string.find(line, "alt='Stable Server") + 19
            if x >= 19:
                temp.stable_server = 1
                line = line[start + 19:]  # line truncated
            # tquery = tquery + str(temp.stable_server) + ', '

            # get authority server
            x = string.find(line, "alt='Authority Server'") + 19
            if x >= 19:
                temp.authority_server = 1
                line = line[start + 19:]  # line truncated
            # tquery = tquery + str(temp.authority_server) + ', '

            # get os
            start = string.find(line, "<img src='img/os-icons/") + 23
            end = string.find(line, ".png", start)
            if start >= 23:
                temp.os = line[start:end]
                line = line[end:]  # line truncated
            # tquery = tquery + '"' + temp.os + '"' + ', '

            # get version
            start = string.find(line, "' title='Tor ") + 13
            end = string.find(line, " on ", start)
            if start >= 13:
                temp.version = line[start:end]
                line = line[end:]  # line truncated
            # tquery = tquery + '"' + temp.version + '"' + ', '

            # get or-port Server
            start = string.find(line, "</table></td><td class='TDc'><b>") + 32
            if start >= 32:
                end = string.find(line, "</b>", start)
                temp.ORPort = line[start:end]
                line = line[end:]  # line truncated

            else:
                start = string.find(line, "</table></td><td class='TDc'>") + 29
                end = string.find(line, "<", start)
                if start >= 29:
                    temp.ORPort = line[start:end]
                    line = line[end:]  # line truncated
            # tquery = tquery + '"' + temp.ORPort + '"' + ', '

            # get dir-port Server
            start = string.find(line, "<td class='TDc'><b>") + 19
            if start >= 19:
                end = string.find(line, "</b></td><td class='F", start)
                temp.DirPort = line[start:end]
                line = line[end:]  # line truncated
            else:
                start = string.find(line, "<td class='TDc'>") + 16
                end = string.find(line, "</td><td class='F", start)
                if start >= 16:
                    temp.DirPort = line[start:end]
                    line = line[end:]  # line truncated
            # tquery = tquery + str(temp.DirPort) + ', '

            # get bad-exit
            if string.find(line, "<td class='F0'") >= 0:
                temp.bad_exit = 0
            elif string.find(line, "<td class='F1'") >= 0:
                temp.bad_exit = 1
            else:
                temp.bad_exit = -1

            # tquery += str(temp.bad_exit)


            # get router specific details
            page = urllib2.urlopen('https://torstatus.blutmagie.de/router_detail.php?FP=' + temp.hash)
            data = page.read()

            # read Last descriptor published date
            start = string.find(data, "Last Descriptor Published (GMT):") + 59
            end = string.find(data, "</td>", start)
            if start >= 58:
                temp.descriptor_publish_date = data[start:end]
                data = data[end:]  # line truncated

            # bandwidth detailed
            start = string.find(data, "<b>Bandwidth (Max/Burst/Observed - In Bps):</b></td>") + 70
            if start >= 70:
                # get bw_max
                end1 = string.find(data, "&nbsp;/", start)
                temp.bw_max = data[start:end1]
                data = data[end1:]  # line truncated

                # get bw_burst
                start = 13
                end1 = string.find(data, "&nbsp;/", start)
                temp.bw_burst = data[start:end1]
                data = data[end1:]  # line truncated

                # get bw_observed
                start = 13
                end = string.find(data, "</td>", start)
                temp.bw_observed = data[start:end]
                data = data[end:]  # line truncated

            # family not done yet

            # bad_directory
            start = string.find(data, "<td class='TRAR'><b>Bad Directory:</b></td>") + 43
            if start >= 43:
                data = data[start:]
                start = string.find(data, "<td class='F0'>")
                if start < 5:
                    temp.bad_directory = 0
                else:
                    start = string.find(data, "<td class='F1'>")
                    if start < 5:
                        temp.bad_directory = 1

            data = data[start + 16:]  # line truncated

            # exit policy
            start = string.find(data, "Exit Policy Information</td>") + 64
            data = data[start:]  # line truncated
            end = string.find(data, "</td>")
            if start >= 64:
                temp.exit_policy = data[0:end]
                temp.exit_policy = string.replace(temp.exit_policy, '</b>', '')  # clean </b>
                temp.exit_policy = string.replace(temp.exit_policy, '<br/>', ',')  # clean <br/>
                temp.exit_policy = string.replace(temp.exit_policy, '\n', '')  # clean \n
                temp.exit_policy = temp.exit_policy[1:len(temp.exit_policy) - 3]
                data = data[end:]  # line truncated

            # temp.exit_policy = temp.exit_policy[0:len(temp.exit_policy)-1]
            print temp.exit_policy

            '''
            soup = BeautifulSoup(page)
            while True:
                x = soup.findall('td', {'class':'TRAR'}).string
                for a in x:
                    if a.b.string=="<b>Last Descriptor Published (GMT):</b>":
                        print a.b.string
                        break



                # get descripter publish date
                start = string.find(line2,"<td class='TRAR'><b>Last Descriptor Published (GMT):</b></td><td class='TRSB'>")+78
                end = string.find(line, "</td>", start)
                if start >= 78:
                    temp.descriptor_publish_date = line[start:end]
                    line = line[end:]  # line truncated

                # get bandwidth details
                start = string.find(line2,"<td class='TRAR'><b>Bandwidth (Max/Burst/Observed - In Bps):</b></td><td class='TRSB'>")+86
                end1 = string.find(line, "/", start)
                if start >= 86:
                    temp.descriptor_publish_date = line[start:end]
                    line = line[end:]  # line truncated

                start = end1+1
                end2 = string.find(line, "/", start)
                end3 = string.find(line, "/", start)

            '''
            tquery = "INSERT INTO tor_nodes SET router_lat='" + str(temp.router_lat) + "',router_long='" + str(
                temp.router_long) + "', router_country='" + temp.router_country + "', hash='" + temp.hash + "', router_name='" + temp.router_name + "', bandwidth='" + str(
                temp.bandwidth) + "', uptime='" + temp.uptime + "', hostname='" + temp.hostname + "', ip='" + temp.ip + "', fast_server='" + str(
                temp.fast_server) + "', exit_server='" + str(temp.exit_server) + "', directory_server='" + str(
                temp.directory_server) + "', guard_server='" + str(temp.guard_server) + "', stable_server='" + str(
                temp.stable_server) + "', authority_server='" + str(
                temp.authority_server) + "', os='" + temp.os + "', version='" + temp.version + "', ORPort='" + str(
                temp.ORPort) + "', DirPort='" + str(temp.DirPort) + "', bad_exit='" + str(
                temp.bad_exit) + "', discriptor_publish_date='" + temp.descriptor_publish_date + "',bw_max='" + str(
                temp.bw_max) + "',bw_burst='" + str(temp.bw_burst) + "',bw_observed='" + str(
                temp.bw_observed) + "',bad_directory='" + str(
                temp.bad_directory) + "',exit_policy='" + temp.exit_policy + "'"
            nodes_list.append(temp)
            # query = query + tquery + "),"

            try:
                conn.query(tquery)
                i += 1
                print i, "completed"
            except mysql.Error, e:
                print e

    conn.close()

    '''
    print tquery


    x = string.rfind(query,"(")
    query = query[0:x]
    query = string.rstrip(query, ',')
    query += "]"

    f = open("tornodes.sql","w")
    if f:
        f.write(tquery)
    f.close()

    '''
    return nodes_list

    '''
    lists = ['http://torstatus.blutmagie.de/']
    allexits = []
    allgaurds = []
    allrelays = []

    for exitlist in lists:
        for line in urllib2.urlopen(exitlist):
            sys.stdin.readline()
            print line


    return allexits


def checkip(address):
    # Global variable prevents secondary scrapes for subsequent checks.
    # Scrape will happen again next time the script runs.
    # Pickle the result if you want to save it for later.
    global exits

    try:  # If doing something to the variable fails, it doesn't exist
        garbage = type(exits)
    except NameError:  # It failed. Let's make it exist.
        exits = fetch()

    return address in exits

'''


if __name__ == "__main__":
    print 'Getting exits, this might take some time...'
    allexits = fetch()
    # for exit in allexits:
    #    print exit
    # print 'There are currently ' + str(len(allexits)) + ' Tor exit nodes.'
    # print 'Also...'
    # while True:
    #    if checkip(raw_input('Enter an IP and I\'ll check it against the list: ')):
    #        print 'Yes, that\'s a Tor exit.'
    #    else:
    #        print 'No, that is not a Tor exit.'
