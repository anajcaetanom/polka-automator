#!/home/p4/src/p4dev-python-venv/bin/python

from automate import *
from aux import *
from polka.tools import calculate_routeid, print_poly

DEBUG = False

if __name__ == "__main__":

    NETWORKX_TOPO = load_topology()

    node_ids = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1], 
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1], 
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1], 
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], 
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1], 
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1], 
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1], 
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1], 
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1], 
    ]

    print("Insering irred poly (node-ID)...")
    attribute_irred_poly_to_nodes(NETWORKX_TOPO, node_ids)

    MININET_TOPO = networkxTopo_to_mininetTopo(NETWORKX_TOPO)

    source = input("\nType the source host (ex: H1): ").upper()
    target = input("Type the target host (ex: H2): ").upper()

    # print all paths between source and target and make the user choose one 
    all_paths = get_all_paths_between_hosts(NETWORKX_TOPO, source, target)
    
    print(f"\nFound {len(all_paths)} paths between {source} and {target}:\n")

    chosen_path = menu(all_paths)

    # ida
    node_ids_path = get_node_ids(NETWORKX_TOPO, chosen_path)
    output_ports = decimal_to_binary(get_output_ports(chosen_path, MININET_TOPO, NETWORKX_TOPO))
    print_poly(calculate_routeid(node_ids_path, output_ports, debug=DEBUG))
    
    # volta
    path_volta = chosen_path[::-1] # ?só inverti o caminho escolhido?
    node_ids_path = get_node_ids(NETWORKX_TOPO, path_volta)
    output_ports = decimal_to_binary(get_output_ports(path_volta, MININET_TOPO, NETWORKX_TOPO))
    print_poly(calculate_routeid(node_ids_path, output_ports, debug=DEBUG))

    # TODO:
        # automatizar a alteração das tabelas de configuração dos edge nodes