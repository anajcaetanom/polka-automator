import networkx
import matplotlib.pyplot as plt

def print_nodes_by_type(topology):
    """
    Print nodes and its attributes.
    """
    for node in topology.nodes():
        attrs = topology.nodes[node]
        print(f"Node {node}:")
        for key, value in attrs.items():
            print(f"  {key}: {value}")
        print()

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