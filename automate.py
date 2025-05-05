#!/home/p4/src/p4dev-python-venv/bin/python

import os
import networkx

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from p4_mininet import P4Switch

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
    Convert a NetworkX topology to a Mininet topology.
    """
    class MininetTopo(Topo):
        def build(self):
            # Add hosts and switches to the Mininet topology
            for node in topology.nodes():
                node_number = get_node_number(node)
                if topology.nodes[node]['type'] == 'host':
                    edge_number = get_connected_edge_number(topology, node)
                    ip = f"10.0.{edge_number}.{node_number}"
                    mac = f"00:00:00:00:{edge_number:02x}:{node_number:02x}"
                    self.addHost(node, ip=ip, mac=mac)

                elif topology.nodes[node]['type'] == 'leaf':
                    # read the network configuration
                    path = os.path.dirname(os.path.abspath(__file__))
                    json_file = path + "/polka/polka-edge.json"
                    config = path + f"/polka/config/e{node_number}-commands.txt"
                    # add P4 switches (core)
                    self.addSwitch(
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
                    self.addSwitch(
                        f"s{node_number}",
                        netcfg=True,
                        json=json_file,
                        thriftport=50000 + node_number,
                        switch_config=config,
                        loglevel='debug',
                        cls=P4Switch,
                    )

            
            # Add links between nodes
            #for u, v in topology.edges():
            #    self.addLink(u, v, bw=10)
    
    return MininetTopo() # retorna uma instancia da topologia mininet

def teste(topology):
    net = Mininet(topo=topology)
    for host in net.hosts:
        print(host)

    for switch in net.switches:
        print(switch)

def run_mininet(topology):
    net = Mininet(topo=topology)
    info("*** Starting network\n")
    net.start()
    net.staticArp()

    # disabling offload for rx and tx on each host interface
    for host in net.hosts:
        host.cmd("ethtool --offload {}-eth0 rx off tx off".format(host.name))

    info("*** Running CLI\n")
    CLI(net)

    os.system("pkill -9 -f 'xterm'")

    info("*** Stopping network\n")
    net.stop()


