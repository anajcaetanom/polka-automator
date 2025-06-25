#!/home/p4/src/p4dev-python-venv/bin/python

from load_topology import *
from aux import *
from polka.tools import calculate_routeid, print_poly, shifting

DEBUG = False

NETWORKX_TOPO = loadNXtopology()

def insertNodeID():
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


if __name__ == "__main__":

    insertNodeID()
    print("\nStarting mininet...")
    MN_NET = loadMininet(NETWORKX_TOPO)
    MN_NET.start()

    print("\nMenu:")
    print("1. Choose a single path.")
    print("2. Generate route-ID for all paths.")
    print("0. Exit.")

    while True:
        try:
            action = int(input("\nSelect an option: "))
            if action == 0:
                print("Exiting...")
                break
            elif action == 1:  
                source = get_host("\nType the source host (ex: h1): ")
                target = get_host("Type the target host (ex: h2): ")

                # print all paths between source and target and let the user choose one.
                all_paths = get_all_paths_between_hosts(NETWORKX_TOPO, source, target)
                
                print(f"\nFound {len(all_paths)} paths between {source} and {target}:\n")

                chosen_path = menu(all_paths)

                ############### IDA ###############
                path_node_ids = get_node_ids(NETWORKX_TOPO, chosen_path)
                port_ids = decimal_to_binary(get_output_ports(chosen_path, MN_NET, NETWORKX_TOPO))
                routeID = calculate_routeid(path_node_ids, port_ids, debug=DEBUG)

                print('\n####### IDA #######\n')
                target_ip = MN_NET.get(target).params['ip'] # ip com a mascara
                print(f"Target IP: {target_ip}")
                output_port = get_leaf_to_core_port_from_path(MN_NET, chosen_path, NETWORKX_TOPO)
                print(f"Output Port: {output_port}")
                target_mac = MN_NET.get(target).MAC()
                print(f"Target MAC: {target_mac}")
                routeID_int = shifting(routeID)
                print(f"RouteID (int): {routeID_int}")

                linha = f"table_add tunnel_encap_process_sr add_sourcerouting_header {target_ip} => {output_port} {target_mac} {routeID_int}"

                node_number = get_node_number(source)
                filename = f'e{node_number}-commands.txt'
                first_line = "table_set_default tunnel_encap_process_sr tdrop"
                if not contains_line(filename, first_line):
                    with open(filename, 'a') as arquivo:  # 'a' = append
                        arquivo.write(first_line)
                with open(filename, 'a') as arquivo:  
                    arquivo.write('\n' + linha)
                
                ############### VOLTA ###############
                path_volta = chosen_path[::-1] # ?só inverti o caminho escolhido?
                path_node_ids = get_node_ids(NETWORKX_TOPO, path_volta)
                port_ids = decimal_to_binary(get_output_ports(path_volta, MN_NET, NETWORKX_TOPO))
                routeID = calculate_routeid(path_node_ids, port_ids, debug=DEBUG)

                print('\n####### VOLTA #######\n')
                target_ip = MN_NET.get(target).params['ip'] 
                print(f"Target IP: {target_ip}")
                output_port = get_leaf_to_core_port_from_path(MN_NET, path_volta, NETWORKX_TOPO)
                print(f"Output Port: {output_port}")
                target_mac = MN_NET.get(source).MAC()
                print(f"Target MAC: {target_mac}")
                routeID_int = shifting(routeID)
                print(f"RouteID (int): {routeID_int}")

                linha = f"table_add tunnel_encap_process_sr add_sourcerouting_header {target_ip} => {output_port} {target_mac} {routeID_int}"

                node_number = get_node_number(target)
                filename = f'e{node_number}-commands.txt'
                first_line = "table_set_default tunnel_encap_process_sr tdrop"
                if not contains_line(filename, first_line):
                    with open(filename, 'a') as arquivo:  # 'a' = append
                        arquivo.write(first_line)
                with open(filename, 'a') as arquivo:  
                    arquivo.write('\n' + linha)

                print('\nInfos adicionadas na tabela.')
                MN_NET.stop()                
                break

            elif action == 2:
                print("\nGenerating IDs for all paths...")
                # TODO:
                    # fazer todas as tabelas de uma vez
                break
        except Exception as e:
            print(f"Error: {e}")
            break 