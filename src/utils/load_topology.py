import os
import networkx

from mn_wifi.net import Mininet_wifi
from mn_wifi.bmv2 import P4Switch

from utils.network_utils import *

def loadNXtopology(file):
    """
    Loads a topology from a GML file.
    """
    # file = 'topology.gml'
    topology = networkx.read_gml(file, label='label')
    return topology

def loadMininet(nx_topology):
    """
    Iniciates a Mininet Wifi network, and constructs the mininet topology based on the NetworkX topology.
    """
    net = Mininet_wifi()
    current_file = os.path.abspath(__file__)
    project_root = os.path.abspath(os.path.join(current_file, "..", ".."))

    for node in nx_topology.nodes():
        config = os.path.join(project_root, "polka", "config", f"{node}-commands.txt")
        node_number = get_node_number(node)

        if nx_topology.nodes[node]['type'] == 'host':
            edge_number = get_connected_edge_number(nx_topology, node)
            ip = f"10.0.{edge_number}.{node_number}"
            mac = f"00:00:00:00:{edge_number:02x}:{node_number:02x}"
            net.addHost(f"{node}", ip=ip, mac=mac)

        elif nx_topology.nodes[node]['type'] == 'leaf':
            # read the network configuration
            json_file = os.path.join(project_root, "polka", "polka-edge.json")
            # add P4 switches (edge)
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
            json_file = os.path.join(project_root, "polka", "polka-core.json")
            # add P4 switches (core)
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
