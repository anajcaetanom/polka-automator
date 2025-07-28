import networkx
import matplotlib.pyplot as plt

def print_nodes_by_type(topology):
    """
    Print nodes by type.
    """
    for node in topology.nodes():
        node_type = topology.nodes[node]['type']
        print(f"Node {node} is of type {node_type}")

def show_nx_topo(topology):
    pos = networkx.spring_layout(topology)
    color_map = []
    for node in topology:
        type = topology.nodes[node].get('type', '')
        if type == 'core':
            color_map.append('blue')
        elif type == 'leaf':
            color_map.append('yellow')
        else:
            color_map.append('gray')

    networkx.draw(
        topology, 
        pos, 
        with_labels=True, 
        node_color=color_map,
        edge_color='lightgray' 
        )
    
    plt.show()