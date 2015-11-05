#!/bin/sh

### set variables
#destinations you don't want routed through Tor
_non_tor="192.168.0.0/16 10.8.0.0/16 192.251.226.204"

#the UID that Tor runs as (varies from system to system)
_tor_uid=$(ps -e | grep ' tor$' | awk '{print $1}')

#Tor's TransPort
_trans_port="9040"
### flush iptables
sudo iptables -F
sudo iptables -t nat -F

#allow clearnet access for hosts in $_non_tor
for _clearnet in $_non_tor 127.0.0.0/9 127.128.0.0/10; do
   iptables -t nat -A OUTPUT -d $_clearnet -j RETURN
done

### set iptables *nat
iptables -t nat -A OUTPUT -m owner --uid-owner $_tor_uid -j RETURN
iptables -t nat -A OUTPUT -p udp --dport 53 -j REDIRECT --to-ports 5333


#redirect all other output to Tor's TransPort
#iptables -t nat -A OUTPUT -p tcp --syn -j REDIRECT --to-ports $_trans_port
#iptables -t nat -A OUTPUT -p tcp -m tcp --dport 1194 -j REDIRECT --to-ports $_trans_port
iptables -t nat -A OUTPUT -p tcp --syn -j REDIRECT --to-ports $_trans_port

#????????????????????????????????????????????????????????????????????????#
# i want to send 1194/tcp traffic to tor and rest of the traffic to tun0
#????????????????????????????????????????????????????????????????????????#

### set iptables *filter
# will allow other established connections to go on and not disconnect them
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

#allow clearnet access for hosts in $_non_tor
for _clearnet in $_non_tor 127.0.0.0/8; do
   iptables -A OUTPUT -d $_clearnet -j ACCEPT
done

#allow only Tor output
iptables -A OUTPUT -m owner --uid-owner $_tor_uid -j ACCEPT
iptables -A OUTPUT -p udp -j REJECT
iptables -A OUTPUT -j REJECT
