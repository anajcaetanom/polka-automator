from automate import *
from aux import *

# topology macro #
NETWORKX_TOPO = load_topology()
# MININET_TOPO = networxTopo_to_mininetTopo(NETWORKX_TOPO)
##################

if __name__ == "__main__":

    # TODO: count the number of core nodes and atribute the polynomial to each node based on the list of irred polynoms
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

    source = input("Type the source host (ex: H1): ").upper()
    target = input("Type the target host (ex: H2): ").upper()

    # print all paths between source and target and make the user choose one #
    all_paths = get_all_paths_between_hosts(NETWORKX_TOPO, source, target)
    
    print(f"Found {len(all_paths)} paths between {source} and {target}:")
    
    for i, path in enumerate(all_paths, 1):
        print(f"Path {i}: {' -> '.join(path)}")
    print("0: Quit")

    chosen_path = menu(all_paths)


    

    # TODO: transmission state (output ports)
      # write the output ports in decimal on the gml file
      # convert to decimal and write the transmission state