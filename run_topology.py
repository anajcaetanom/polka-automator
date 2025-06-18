#!/usr/bin/python

import os
import networkx

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.bmv2 import P4Switch

from load_topology import *
from aux import *

def run_net(net):
    net.start()
    net.staticArp()

    # disabling offload for rx and tx on each host interface
    for host in net.hosts:
        host.cmd("ethtool --offload {}-eth0 rx off tx off".format(host.name))
        # disable ipv6
        host.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        host.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        host.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

    for sw in net.switches:
        sw.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

    info("*** Running CLI\n")
    CLI(net)

    os.system("pkill -9 -f 'xterm'")

    info("*** Stopping network\n")
    net.stop()

if __name__ == "__main__":
    setLogLevel("info")
    nx_topo = loadNXtopology()
    mn_net = loadMininet(nx_topo)
    run_net(mn_net)

