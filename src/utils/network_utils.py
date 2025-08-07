import networkx
import csv
import sys
import ast
import os

def get_node_number(node):
    """
    Gets the number of a node based on its label.
    """
    try:
        return int(node[1:])
    except (ValueError, IndexError) as e:
        print(f"[Error] Failed to parse node number from '{node}': {e}")
        return -1
    

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


def decimal_to_binary(output_ports_list):
    """
    Converts decimal output ports to binary representation.
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
    

def attribute_node_ids(topology, poly_file):
    """
    Attributes irreducible polynomials to core nodes.
    """
    num_core_nodes = sum(1 for n in topology.nodes() if topology.nodes[n].get('type') == 'core')

    irred_polys = []
    with open(poly_file, 'r', encoding='utf-8') as f:
        for i in range(num_core_nodes):
            line = f.readline()
            if not line:
                break
            irred_polys.append(ast.literal_eval(line.strip()))

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


def get_node_ids(topology, chosen_path):
    """
    Gets the node IDs of core nodes in the chosen path.
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


def get_connected_edge_number(topology, node):
    """
    Gets the number of the edge node (leaf) connected to the given node.
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
    Checks whether two hosts are connected to the same leaf.
    """
    try:
        return get_leaf(topology, host1) == get_leaf(topology, host2)
    except Exception as e:
        print(f"[Error] checking if {host1} and {host2} are on the same leaf: {e}")
        return False
    

def get_leaf(topology, host):
    """
    Returns the leaf node connected to the host.
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
    Returns all simple paths between two hosts.
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
    Gets the output port number on node 'src' connected to node 'dst'.
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
    Gets the output ports of the core nodes for a given path in the topology.
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


def extract_polys_from_csv(file_path):
    """
    Extracts irreducible polynomials from a specific CSV file and writes them to 'polynomials.txt'.
    """
    csv.field_size_limit(sys.maxsize)
    
    with open(file_path, newline='') as file:
        reader = csv.reader(file, delimiter=';')
        lines = list(reader)

        if not lines:
            print("[ERROR] Empty CSV file.")
            return []
        
        last_line = lines[-1]
        poly_column = ''.join(last_line[2:]).strip()

        with open('polynomials.txt', 'w', encoding='utf-8') as out:

            if poly_column.startswith('[['):
                poly_column = poly_column[1:]  # agora começa com [

            buffer = ''
            abertos = 0

            for c in poly_column:
                buffer += c
                if c == '[':
                    abertos += 1
                elif c == ']':
                    abertos -= 1
                    if abertos == 0:
                        out.write(buffer.strip().lstrip(', ') + '\n')
                        buffer = ''

    print("Polynomials extracted from CSV.")

if __name__ == '__main__':
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    csv_path = os.path.join(BASE_DIR, "csv", "irr_poly_table1_16.csv")
    extract_polys_from_csv(csv_path)