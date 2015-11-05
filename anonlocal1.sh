#!/bin/sh

### set variables

#Tor's TransPort
_trans_port="9040"

### flush iptables
sudo iptables -F
sudo iptables -t nat -F

### set iptables *nat
iptables -t nat -A OUTPUT -p tcp -m tcp --dport 1194 -j REDIRECT --to-ports $_trans_port

