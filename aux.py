#!/home/p4/src/p4dev-python-venv/bin/python

import networkx
import matplotlib.pyplot as plt

##################################################
#                 aux functions                     
##################################################

def get_node_number(node):
    """
    Get the number of a node based on its label.
    """
    return int(node[1:])

def get_connected_edge_number(topology, node):
    """
    Get the number of the edge node (leaf) connected to the given node.
    Returns None if no edge node is found among neighbors.
    """
    neighbors = list(topology.neighbors(node))
    for neighbor in neighbors:
        if topology.nodes[neighbor]['type'] == 'leaf':
            return get_node_number(neighbor)
    return None

def get_all_paths_between_hosts(topology, host1, host2):
    try:
        # all_simple_paths(): todos os caminhos onde cada nó aparece no máximo uma vez.
        all_paths = list(networkx.all_simple_paths(topology, source=host1, target=host2))

        if not all_paths:
            print("No paths found between the hosts.")
            return []
        else:
            return all_paths
    
    except networkx.NetworkXNoPath:
        print("There are no valid paths between the hosts.")
        return []
    except networkx.NodeNotFound as e:
        print(f"Node not found: {e}")
        return []
    
def attribute_irred_poly_to_nodes(topology, irred_polys):
    """
    Attribute irreducible polynomials to core nodes.
    """
    i = 0
    for node in topology.nodes():
        if topology.nodes[node].get('type') == 'core':
            topology.nodes[node]['node_id'] = irred_polys[i]
            i += 1

def menu(all_paths):
    """
    Display a menu for the user to choose a path and return the chosen path.
    """

    for i, path in enumerate(all_paths, 1):
        print(f"Path {i}: {' -> '.join(path)}")
    
    while True:
        try:
            option = int(input("\nType the number of a path to choose, or 0 to quit: "))
            if (option == 0):
                print("Exiting...")
                break
            elif (1 <= option <= len(all_paths)):
                chosen_path = all_paths[option - 1]
                print(f"You chose path {option}.\n")
                return chosen_path
            else:
                print("Invalid option. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_output_ports(path, topology, nx_topo):
    """
    Get the output ports of the core nodes for a given path in the topology.
    """
    output_ports = []
    for i in range(len(path)-1):
        current_node = path[i]
        next_node = path[i+1]
        
        if nx_topo.nodes[current_node].get('type') == 'core':
            port = topology.port(current_node, next_node)
            if isinstance(port, tuple):
                output_ports.append(port[0]) # coloca só a porta de saída na lista
            else:
                output_ports.append(port)

    return output_ports

def decimal_to_binary(output_ports_list):
    """
    Convert decimal output ports to binary representation.
    """
    binary_list = []
    for port in output_ports_list:
        binary = bin(port)[2:]
        digits = [int(p) for p in binary]
        binary_list.append(digits)

    return binary_list

def get_node_ids(topology, chosen_path):
    """
    Get the node IDs of core nodes in the chosen path.
    """
    node_list = []
    for node in chosen_path:
        if topology.nodes[node].get('type') == 'core':
            node_id = topology.nodes[node].get('node_id')
            node_list.append(node_id)

    return node_list
        
############### funçoes de teste #####################
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