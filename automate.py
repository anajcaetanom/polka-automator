import os
import networkx

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from mininet.cli import CLI

def load_topology():
    """
    Load a topology from a GML file.
    """
    file = 'topology.gml'
    topology = networkx.read_gml(file, label='label')
    return topology

def networxTopo_to_mininetTopo(topology):
    """
    Convert a NetworkX topology to a Mininet topology.
    """
    class MininetTopo(Topo):
        def build(self):
            # Add hosts and switches to the Mininet topology
            for node in topology.nodes():
                node_number = get_node_number(topology, node)
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
            for u, v in topology.edges():
                self.addLink(u, v, bw=10)
    
    return MininetTopo() # retorna uma instancia da topologia mininet

def run_mininet():
    networkx_topo = load_topology()
    topo = networxTopo_to_mininetTopo(networkx_topo)
    net = Mininet(topo=topo)
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



##################################################
#                 aux functions                     
##################################################

def get_node_number(topology, node):
    """
    Get the number of a node based on its label.
    """
    label = topology.nodes[node]['label']
    return int(label[1:])

def get_connected_edge_number(topology, node):
    """
    Get the number of the edge node (leaf) connected to the given node.
    Returns None if no edge node is found among neighbors.
    """
    neighbors = list(topology.neighbors(node))
    for neighbor in neighbors:
        if topology.nodes[neighbor]['type'] == 'leaf':
            return get_node_number(topology, neighbor)
    return None

def get_path_between_hosts(topology, host1, host2):
    try:
        path = networkx.shortest_path(topology, source=host1, target=host2)
        core_nodes = [n for n in path if n.startswith("E") and n[1:].isdigit()]
        return core_nodes
    except networkx.NetworkXNoPath:
        print("Não há caminho entre os hosts.")
        return []