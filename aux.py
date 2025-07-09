#!/home/p4/src/p4dev-python-venv/bin/python

import re
import networkx
import ipaddress
import matplotlib.pyplot as plt

##################################################
#                    UTILS                       
##################################################

def get_node_number(node):
    """
    Get the number of a node based on its label.
    """
    try:
        return int(node[1:])
    except (ValueError, IndexError) as e:
        print(f"[Error] Failed to parse node number from '{node}': {e}")
        return -1

def contains_line(filename, target_line):
    """
    Check if a file contains a specific line.
    """
    try:
        with open(filename, 'r') as file:
            return any(line.strip() == target_line for line in file)
    except FileNotFoundError:
        print(f"[Error] File not found: {filename}")
        return False
    except Exception as e:
        print(f"[Error] while checking line in file: {e}")
        return False

def clean_and_sort_file(caminho_arquivo):
    """
    Remove empty lines and sort the remaining ones based on IP addresses.
    """
    try:
        with open(caminho_arquivo, 'r') as f:
            linhas = f.readlines()
        if not linhas:
            return  # arquivo vazio, nada a fazer

        primeira_linha = linhas[0].rstrip('\n')

        def extract_ip(linha):
            partes = linha.split()
            for parte in partes:
                if '/' in parte:
                    try:
                        return ipaddress.ip_network(parte, strict=False)
                    except ValueError:
                        continue
            return ipaddress.ip_network("255.255.255.255/32") # fallback

        resto_linhas = [linha.strip() for linha in linhas[1:] if linha.strip() != '']
        resto_linhas.sort(key=extract_ip)
        linhas_final = [primeira_linha] + resto_linhas

        with open(caminho_arquivo, 'w') as f:
            for linha in linhas_final:
                f.write(linha + '\n')
    
    except Exception as e:
        print(f"[Error] while cleaning and sorting file: {e}")

##################################################
#              NETWORK TOPOLOGY                 
##################################################

def attribute_node_ids(topology, irred_polys):
    """
    Attribute irreducible polynomials to core nodes.
    """
    try:
        i = 0
        for node in topology.nodes():
            if topology.nodes[node].get('type') == 'core':
                topology.nodes[node]['node_id'] = irred_polys[i]
                i += 1
    except IndexError:
        print("[Error] Not enough irreducible polynomials for all core nodes.")
    except Exception as e:
        print(f"[Error] while assigning node_ids: {e}")

def hex_node_id(node_id):
    """
    Converts a binary node_id to a hexadecimal string.
    """
    try:
        # Remove the first occurrence of 1
        idx = node_id.index(1)
        trimmed = node_id[idx + 1:]

        # Convert to binary string, then to int, then to hex with zero-padding
        bin_str = ''.join(str(b) for b in trimmed)
        hex_value = int(bin_str, 2)
        return f"0x{hex_value:04x}"
    except ValueError:
        print("[Error] No '1' found in node_id.")
    except Exception as e:
        print(f"[Error] while converting node_id to hex: {e}")


def get_connected_edge_number(topology, node):
    """
    Get the number of the edge node (leaf) connected to the given node.
    Returns None if no edge node is found among neighbors.
    """
    try: 
        neighbors = list(topology.neighbors(node))
        for neighbor in neighbors:
            if topology.nodes[neighbor]['type'] == 'leaf':
                return get_node_number(neighbor)
    except Exception as e:
        print(f"[Error] while getting connected leaf: {e}")
    return None

def connected_to_same_leaf(topology, host1, host2):
    """
    Check whether two hosts are connected to the same leaf.
    """
    try:
        return get_leaf(topology, host1) == get_leaf(topology, host2)
    except Exception as e:
        print(f"[Error] checking if {host1} and {host2} are on the same leaf: {e}")
        return False

def get_leaf(topology, host):
    """
    Return the leaf node connected to the host.
    """
    try:
        vizinhos = list(topology.neighbors(host))
        for vizinho in vizinhos:
            if topology.nodes[vizinho].get("type") == "leaf":
                return vizinho
    except Exception as e:
        print(f"[Error] while searching leaf of {host}: {e}")
    return None

def get_all_paths_between_hosts(topology, host1, host2):
    """
    Return all simple paths between two hosts.
    """
    try:
        # all_simple_paths(): todos os caminhos onde cada nó aparece no máximo uma vez.
        all_paths = list(networkx.all_simple_paths(topology, host1, host2))
        if not all_paths:
            print("No paths found between the hosts.")
            return []
        else:
            return all_paths
    except networkx.NetworkXNoPath:
        print("There are no valid paths between the hosts.")
    except networkx.NodeNotFound as e:
        print(f"Node not found: {e}")
    except Exception as e:
        print(f"[Error] while retrieving paths: {e}")
    return []

def get_output_port(net, src, dst, debug=False):
    """
    Get the output port number on node 'src' connected to node 'dst'.
    """
    try:
        src_node = net.get(src)
        dst_node = net.get(dst)
        if not src_node or not dst_node:
            raise ValueError(f"One of the nodes ({src}, {dst}) not found.")

        for intf in src_node.intfList():
            if not intf.link:
                continue
            try:
                peer_intf = intf.link.intf1 if intf.link.intf1.node != src_node else intf.link.intf2
                if peer_intf.node == dst_node:
                    if debug:
                        print(f"[DEBUG] Interface {intf.name} connects {src} -> {dst}")
                    if intf.name and 'eth' in intf.name:
                        return int(intf.name.split('eth')[-1])
                    else:
                        return src_node.intfList().index(intf)
            except Exception as e:
                if debug:
                    print(f"[DEBUG] Error accessing peer of {intf.name}: {e}")
                continue

        raise Exception(f"{src} is not directly connected to {dst}")

    except Exception as e:
        print(f"[Error] while getting output port from {src} to {dst}: {e}")
        return None

def get_output_ports_list(path, net, nx_topo):
    """
    Get the output ports of the core nodes for a given path in the topology.
    """
    try:
        output_ports = []
        for i in range(len(path) - 1):
            current_node = path[i]
            next_node = path[i + 1]

            if nx_topo.nodes[current_node].get('type') == 'core':
                port = get_output_port(net, current_node, next_node)
                output_ports.append(port)
        return output_ports
    except Exception as e:
        print(f"[Error] while getting output ports: {e}")
        return []

def get_node_ids(topology, chosen_path):
    """
    Get the node IDs of core nodes in the chosen path.
    """
    try:
        node_list = []
        for node in chosen_path:
            if topology.nodes[node].get('type') == 'core':
                node_id = topology.nodes[node].get('node_id')
                node_list.append(node_id)
        return node_list
    except KeyError as e:
        print(f"[Error] node_id not found in topology: {e}")
    except Exception as e:
        print(f"[Error] while retrieving node_ids: {e}")
    return []

def get_leaf_to_core_port_from_path(net, path, topo_nx):
    """
    From a given path, identifies the leaf node and returns the output port to the core.
    """
    try:
        for i in range(len(path) - 1):
            curr_node = path[i]
            next_node = path[i + 1]

            if topo_nx.nodes[curr_node].get("type") == "leaf" and topo_nx.nodes[next_node].get("type") == "core":
                return get_output_port(net, curr_node, next_node)

    except Exception as e:
        print(f"[Error] while finding leaf-to-core port: {e}")
    print("No leaf-to-core hop found in the path.")
    return None

def decimal_to_binary(output_ports_list):
    """
    Convert decimal output ports to binary representation.
    """
    try:
        binary_list = []
        for port in output_ports_list:
            binary = bin(port)[2:]
            digits = [int(p) for p in binary]
            binary_list.append(digits)
        return binary_list
    except Exception as e:
        print(f"[Error] while converting ports to binary: {e}")
        return []

##################################################
#                USER INTERFACE                 
##################################################

def get_host(prompt):
    """
    Get a valid host input from the user.
    """
    while True:
        try:
            host = input(prompt).strip().lower()
            if re.fullmatch(r"h\d+", host):
                return host
            else:
                print("Invalid input. Please type a valid host like 'h1', 'h2', ...")
        except Exception as e:
            print(f"[Error] while reading input: {e}")

def menu1():
    """
    Main menu selection.
    """
    while True:
        try:
            print("\nMenu:")
            print("1. Choose a single path.")
            print("2. Generate route-ID for all paths.")
            print("3. Empty all edge tables.")
            print("0. Exit.")

            action = input("\nSelect an option: ").strip()

            if action in ('0', '1', '2', '3'):
                return int(action)
            else:
                print("Invalid option. Please enter 0, 1, 2 or 3.")
        except Exception as e:
            print(f"[Error] in menu1: {e}")

def menu2(all_paths):
    """
    Allow user to select one of the listed paths.
    """
    try:
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
    except Exception as e:
        print(f"[Error] in menu2: {e}")
        return None

##################################################
#               DEBUG / TEST                 
##################################################

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