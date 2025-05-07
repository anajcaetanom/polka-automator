#!/home/p4/src/p4dev-python-venv/bin/python

import networkx

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
    print("0: Quit")
    
    while True:
        try:
            option = int(input("Type the number of a path to choose, or 0 to quit: "))
            if (option == 0):
                print("Exiting...")
                break
            elif (1 <= option <= len(all_paths)):
                chosen_path = all_paths[option - 1]
                print(f"You chose path {option}.")
                return chosen_path
            else:
                print("Invalid option. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_output_ports(path, net):
    output_ports = []
    for i in range(len(path)-1):
        current_node = path[i]
        next_node = path[i+1]
        
        # Verificando qual porta do switch leva ao próximo nó
        #for port, intf in net.get(current_node).intfs.items():
        #    if next_node in str(intf):
        #        output_ports.append(port)
        #        print(f"Switch {current_node} usa a porta {port} para alcançar {next_node}.")

############### funçoes de teste #####################
def print_nodes_by_type(topology):
    """
    Print nodes by type.
    """
    for node in topology.nodes():
        node_type = topology.nodes[node]['type']
        print(f"Node {node} is of type {node_type}")