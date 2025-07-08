import os
import networkx

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.bmv2 import P4Switch

from aux import *

def loadNXtopology():
    """
    Load a topology from a GML file.
    """
    file = 'topology.gml'
    topology = networkx.read_gml(file, label='label')
    return topology

def loadMininet(nx_topology):
    """
    Iniciates a Mininet Wifi network, and constructs the mininet topology based on the NetworkX topology.
    """
    net = Mininet_wifi()

    for node in nx_topology.nodes():
        node_number = get_node_number(node)

        if nx_topology.nodes[node]['type'] == 'host':
            edge_number = get_connected_edge_number(nx_topology, node)
            ip = f"10.0.{edge_number}.{node_number}"
            mac = f"00:00:00:00:{edge_number:02x}:{node_number:02x}"
            net.addHost(f"{node}", ip=ip, mac=mac)

        elif nx_topology.nodes[node]['type'] == 'leaf':
            # read the network configuration
            path = os.path.dirname(os.path.abspath(__file__))
            json_file = path + "/polka/polka-edge.json"
            config = path + f"/polka/config/{node}-commands.txt"
            # add P4 switches (core)
            net.addSwitch(
                f"{node}",
                netcfg=True,
                json=json_file,
                thriftport=50100 + node_number,
                switch_config=config,
                loglevel='debug',
                cls=P4Switch,
            )

        elif nx_topology.nodes[node]['type'] == 'core':
            # read the network configuration
            path = os.path.dirname(os.path.abspath(__file__))
            json_file = path + "/polka/polka-core.json"
            config = path + f"/polka/config/{node}-commands.txt"
            # Add P4 switches (core)
            net.addSwitch(
                f"{node}",
                netcfg=True,
                json=json_file,
                thriftport=50000 + node_number,
                switch_config=config,
                loglevel='debug',
                cls=P4Switch,
            )

    # Add links between nodes
    for u, v in nx_topology.edges():
        net.addLink(u, v, bw=10)

    return net  

