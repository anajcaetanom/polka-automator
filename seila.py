import os
import networkx


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
    from mininet.topo import Topo
    
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
                    config = path + "/polka/config/e{}-commands.txt".format(node_number)
                    # add P4 switches (core)
                    self.addSwitch(
                        "e{}".format(node),
                        netcfg=True,
                        json=json_file,
                        thriftport=50100 + int(node_number),
                        switch_config=config,
                        loglevel='debug',
                        cls=P4Switch,
                    )

                elif topology.nodes[node]['type'] == 'core':
                    # read the network configuration
                    path = os.path.dirname(os.path.abspath(__file__))
                    json_file = path + "/polka/polka-core.json"
                    config = path + "/polka/config/s{}-commands.txt".format(node_number)
                    # Add P4 switches (core)
                    self.addSwitch(
                        node,
                        netcfg=True,
                        json=json_file,
                        thriftport=50000 + int(node_number),
                        switch_config=config,
                        loglevel='debug',
                        cls=P4Switch,
                    )

            # Add links between nodes
            for u, v in topology.edges():
                self.addLink(u, v)
    return MininetTopo()

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