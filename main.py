#!/home/p4/src/p4dev-python-venv/bin/python

from automate import *
from aux import *
from polka.tools import calculate_routeid, print_poly

DEBUG = False

if __name__ == "__main__":

    NETWORKX_TOPO = load_topology()

    # nodeID: an identifier previously assigned to core nodes 
    #         by the controller in a network configuration phase
    irred_polys = [
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

    print("\nInsering irred poly (node-ID)...")
    attribute_node_ids(NETWORKX_TOPO, irred_polys)

    MININET_TOPO = networkxTopo_to_mininetTopo(NETWORKX_TOPO)

    source = get_host("\nType the source host (ex: H1): ")
    target = get_host("Type the target host (ex: H2): ")

    # print all paths between source and target and make the user choose one 
    all_paths = get_all_paths_between_hosts(NETWORKX_TOPO, source, target)
    
    print(f"\nFound {len(all_paths)} paths between {source} and {target}:\n")

    chosen_path = menu(all_paths)

    # ida
    path_node_ids = get_node_ids(NETWORKX_TOPO, chosen_path)
    port_ids = decimal_to_binary(get_output_ports(chosen_path, MININET_TOPO, NETWORKX_TOPO))
    print_poly(calculate_routeid(path_node_ids, port_ids, debug=DEBUG))
    
    # volta
    path_volta = chosen_path[::-1] # ?só inverti o caminho escolhido?
    path_node_ids = get_node_ids(NETWORKX_TOPO, path_volta)
    port_ids = decimal_to_binary(get_output_ports(path_volta, MININET_TOPO, NETWORKX_TOPO))
    print_poly(calculate_routeid(path_node_ids, port_ids, debug=DEBUG))

    # TODO:
        # automatizar a alteração das tabelas de configuração dos edge nodes