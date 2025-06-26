#!/home/p4/src/p4dev-python-venv/bin/python

import re
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
    
def attribute_node_ids(topology, irred_polys):
    """
    Attribute irreducible polynomials to core nodes.
    """
    i = 0
    for node in topology.nodes():
        if topology.nodes[node].get('type') == 'core':
            topology.nodes[node]['node_id'] = irred_polys[i]
            i += 1

def get_host(prompt):
    """
    Get a valid host input from the user.
    """
    while True:
        host = input(prompt).strip().lower()
        if re.fullmatch(r"h\d+", host):
            return host
        else:
            print("Invalid input. Please type a valid host like 'h1', 'h2', ...")

def menu1():
    while True:
        print("\nMenu:")
        print("1. Choose a single path.")
        print("2. Generate route-ID for all paths.")
        print("0. Exit.")

        action = input("\nSelect an option: ").strip()

        if action in ('0', '1', '2'):
            return int(action)
        else:
            print("Invalid option. Please enter 0, 1 or 2.")

def menu2(all_paths):
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

def get_output_port(net, src, dst):
    """
    Returns the output port number of the node 'src' towards the node 'dst'.
    """
    try:
        # output interface from src to dst
        intf = net.get(src).connectionsTo(net.get(dst))[0][0]
        # port number (e.g., s1-eth1 → 1)
        return int(intf.name.split('-')[-1].replace('eth', ''))
    except IndexError:
        raise Exception(f"No connection found between {src} and {dst}.")
    except Exception as e:
        raise Exception(f"Error getting port from {src} to {dst}: {e}")

def get_output_ports(path, net, nx_topo):
    """
    Get the output ports of the core nodes for a given path in the topology.
    """
    output_ports = []
    for i in range(len(path) - 1):
        current_node = path[i]
        next_node = path[i + 1]

        if nx_topo.nodes[current_node].get('type') == 'core':
            port = get_output_port(net, current_node, next_node)
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

def get_leaf_to_core_port_from_path(net, path, topo_nx):
    """
    From a given path, identifies the leaf node and returns the output port to the core.
    """
    for i in range(len(path) - 1):
        curr_node = path[i]
        next_node = path[i + 1]

        if topo_nx.nodes[curr_node].get("type") == "leaf" and topo_nx.nodes[next_node].get("type") == "core":
            leaf = net.get(curr_node)
            core = net.get(next_node)

            links = leaf.connectionsTo(core)
            for intf1, intf2 in links:
                if intf1.node == leaf:
                    port_number = leaf.ports[intf1]
                    return port_number

    print("No leaf-to-core hop found in the path.")
    return None

def contains_line(filename, target_line):
    try:
        with open(filename, 'r') as file:
            for line in file:
                if line.strip() == target_line:
                    return True
        return False
    except FileNotFoundError:
        return False

def get_ip_com_mascara(host):
    """
    Retorna o IP com máscara CIDR de um host Mininet.'
    """
    intf = host.defaultIntf().name
    output = host.cmd(f"ip addr show {intf}")
    match = re.search(r'inet (\d+\.\d+\.\d+\.\d+/\d+)', output)
    return match.group(1) if match else None

def limpar_e_ordenar_arquivo(caminho_arquivo):
    with open(caminho_arquivo, 'r') as f:
        linhas = f.readlines()

    if not linhas:
        return  # arquivo vazio, nada a fazer

    primeira_linha = linhas[0].rstrip('\n')

    # remove linhas em branco (ou só espaços) das linhas seguintes
    resto_linhas = [linha.strip() for linha in linhas[1:] if linha.strip() != '']

    # ordena as linhas restantes alfabeticamente
    resto_linhas.sort()

    # junta tudo com quebras de linha, mantendo a primeira linha
    linhas_final = [primeira_linha] + resto_linhas

    with open(caminho_arquivo, 'w') as f:
        for linha in linhas_final:
            f.write(linha + '\n')
        
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