#!/home/p4/src/p4dev-python-venv/bin/python

import os
import networkx

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.bmv2 import P4Switch

from mininet.net import Mininet
from mininet.topo import Topo

from aux import *

def load_topology():
    """
    Load a topology from a GML file.
    """
    file = 'topology.gml'
    topology = networkx.read_gml(file, label='label')
    return topology

def networkxTopo_to_mininetTopo(topology):
    """
    Iniciates a Mininet Wifi network, and constructs the mininet topology based on the NetworkX topology.
    """
    net = Mininet_wifi()

    for node in topology.nodes():
        node_number = get_node_number(node)

        if topology.nodes[node]['type'] == 'host':
            edge_number = get_connected_edge_number(topology, node)
            ip = f"10.0.{edge_number}.{node_number}"
            mac = f"00:00:00:00:{edge_number:02x}:{node_number:02x}"
            net.addHost(f"h{node_number}", ip=ip, mac=mac)

        elif topology.nodes[node]['type'] == 'leaf':
            # read the network configuration
            path = os.path.dirname(os.path.abspath(__file__))
            json_file = path + "/polka/polka-edge.json"
            config = path + f"/polka/config/e{node_number}-commands.txt"
            # add P4 switches (core)
            net.addSwitch(
                f"e{node_number}",
                netcfg=True,
                json=json_file,
                thriftport=50100 + node_number,
                switch_config=config,
                loglevel='debug',
                cls=P4Switch,
            )

        elif topology.nodes[node]['type'] == 'core':
            # read the network configuration
            path = os.path.dirname(os.path.abspath(__file__))
            json_file = path + "/polka/polka-core.json"
            config = path + f"/polka/config/s{node_number}-commands.txt"
            # Add P4 switches (core)
            net.addSwitch(
                f"s{node_number}",
                netcfg=True,
                json=json_file,
                thriftport=50000 + node_number,
                switch_config=config,
                loglevel='debug',
                cls=P4Switch,
            )

    # Add links between nodes
    for u, v in topology.edges():
        net.addLink(u, v, bw=10)

    return net  

def run_net():
    nx_topo = load_topology()
    net = networkxTopo_to_mininetTopo(nx_topo)
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
    run_net()

