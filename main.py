import os
import subprocess

from load_topology import loadNXtopology, loadMininet
from run_topology import run_net
from utils.user_interface import *
from utils.network_utils import *
from utils.file_utils import *
from utils.test_utils import show_nx_topo

from mininet.log import setLogLevel
from mininet.cli import CLI
from polka.tools import calculate_routeid, shifting

DEBUG = False

if __name__ == "__main__":

    topo = choose_topo_menu() 
    NETWORKX_TOPO = loadNXtopology(topo)

    attribute_node_ids(NETWORKX_TOPO, "polynomials.txt")

    print("\nStarting mininet...")
    MN_NET = loadMininet(NETWORKX_TOPO)
    run_net(MN_NET)

    while True:
        try:
            action = menu1()
            if action == 0:
                print('Stopping and cleaning mininet...')
                MN_NET.stop()
                subprocess.run(['sudo', 'mn', '-c']) 
                print("Exiting...")
                break

            elif action == 1:  
                pasta = os.path.join(os.getcwd(), "polka", "config")
                if not os.path.exists(pasta):
                    os.makedirs(pasta)

                source = get_host("\nType the source host (ex: h1): ")
                target = get_host("Type the target host (ex: h2): ")

                # print all paths between source and target and let the user choose one.
                all_paths = get_all_paths_between_hosts(NETWORKX_TOPO, source, target)
                
                print(f"\nFound {len(all_paths)} paths between {source} and {target}:\n")

                ############### IDA ###############
                chosen_path = menu2(all_paths)
                if chosen_path == 0:
                    continue

                ################ core nodes ################
                for node in chosen_path:
                    if NETWORKX_TOPO.nodes[node]['type'] == 'core':
                        node_id = NETWORKX_TOPO.nodes[node]['node_id']
                        hex_node = hex_node_id(node_id)
                        linha = f"set_crc16_parameters calc {hex_node} 0x0 0x0 false false"
                        filename = f'{node}-commands.txt'
                        complete_path = os.path.join(pasta, filename)
                        if not contains_line(complete_path, linha):
                            with open(complete_path, 'w') as arquivo:
                                arquivo.write(linha)
                
                ################# edge nodes #################  
                path_node_ids = get_node_ids(NETWORKX_TOPO, chosen_path)
                port_ids = decimal_to_binary(get_output_ports_list(chosen_path, MN_NET, NETWORKX_TOPO))
                routeID = calculate_routeid(path_node_ids, port_ids, debug=DEBUG)
                target_ip = MN_NET.get(target).IP() 
                output_port = get_leaf_to_core_port_from_path(MN_NET, chosen_path, NETWORKX_TOPO)
                target_mac = MN_NET.get(target).MAC()
                routeID_int = shifting(routeID)

                linha = f"table_add tunnel_encap_process_sr add_sourcerouting_header {target_ip}/32 => {output_port} {target_mac} {routeID_int}"

                second_node = chosen_path[1]
                if NETWORKX_TOPO.nodes[second_node].get('type') == 'leaf':
                    node_number = get_node_number(second_node)
                filename = f'e{node_number}-commands.txt'
                complete_path = os.path.join(pasta, filename)
                first_line = "table_set_default tunnel_encap_process_sr tdrop"
                if not contains_line(complete_path, first_line):
                    with open(complete_path, 'a') as arquivo:  # 'a' = append
                        arquivo.write(first_line)
                if not contains_line(complete_path, linha):
                    with open(complete_path, 'a') as arquivo:  
                        arquivo.write('\n' + linha)
                    clean_and_sort_file(complete_path)
                    print('\nInfos adicionadas na tabela.')
                else:
                    print("Table already contains that line.")
                
                ############### VOLTA ###############
                path_volta = chosen_path[::-1] # ?só inverti o caminho escolhido?
                path_node_ids = get_node_ids(NETWORKX_TOPO, path_volta)
                port_ids = decimal_to_binary(get_output_ports_list(path_volta, MN_NET, NETWORKX_TOPO))
                routeID = calculate_routeid(path_node_ids, port_ids, debug=DEBUG)
                target_ip = MN_NET.get(source).IP()
                output_port = get_leaf_to_core_port_from_path(MN_NET, path_volta, NETWORKX_TOPO)
                target_mac = MN_NET.get(source).MAC()
                routeID_int = shifting(routeID)

                linha = f"table_add tunnel_encap_process_sr add_sourcerouting_header {target_ip}/32 => {output_port} {target_mac} {routeID_int}"

                second_node = chosen_path[1]
                if NETWORKX_TOPO.nodes[second_node].get('type') == 'leaf':
                    node_number = get_node_number(second_node)
                filename = f'e{node_number}-commands.txt'
                complete_path = os.path.join(pasta, filename)
                first_line = "table_set_default tunnel_encap_process_sr tdrop"
                if not contains_line(complete_path, first_line):
                    with open(complete_path, 'a') as arquivo:  # 'a' = append
                        arquivo.write(first_line)
                if not contains_line(complete_path, linha):
                    with open(complete_path, 'a') as arquivo:
                        arquivo.write('\n' + linha)
                    clean_and_sort_file(complete_path)
                    print('\nInfos adicionadas na tabela.')
                else:
                    print("Table already contains that line.")

            elif action == 2:
                print("\nGenerating IDs for all paths...\n")
                pasta = os.path.join(os.getcwd(), "polka", "config")
                if not os.path.exists(pasta):
                    os.makedirs(pasta)

                ################# edge nodes #################
                hosts = MN_NET.hosts
                comandos_por_arquivo = {}    

                for i in range(len(hosts)):
                    for j in range(len(hosts)):
                        source = hosts[i].name
                        target = hosts[j].name

                        print(f"\nSource: {source}")
                        print(f"Target: {target}\n")

                        all_paths = get_all_paths_between_hosts(NETWORKX_TOPO, source, target)

                        if source == target:
                            path = []
                            path.append(source)
                            leaf = get_leaf(NETWORKX_TOPO, source)
                            path.append(leaf)
                            path.append(target)
                            all_paths.append(path)

                        if not all_paths:
                            continue

                        for path in all_paths:
                            chosen_path = path

                            if connected_to_same_leaf(NETWORKX_TOPO, source, target):
                                routeID_int = 0
                                output_port = get_output_port(MN_NET, chosen_path[1], target)
                            else:
                                path_node_ids = get_node_ids(NETWORKX_TOPO, chosen_path)
                                port_ids = decimal_to_binary(get_output_ports_list(chosen_path, MN_NET, NETWORKX_TOPO))
                                routeID = calculate_routeid(path_node_ids, port_ids, debug=DEBUG)
                                routeID_int = shifting(routeID)
                                output_port = get_leaf_to_core_port_from_path(MN_NET, chosen_path, NETWORKX_TOPO)

                            target_ip = MN_NET.get(target).IP()
                            target_mac = MN_NET.get(target).MAC()

                            linha = f"table_add tunnel_encap_process_sr add_sourcerouting_header {target_ip}/32 => {output_port} {target_mac} {routeID_int}"

                            if chosen_path[1]:
                                second_node = chosen_path[1]
                                if NETWORKX_TOPO.nodes[second_node].get('type') == 'leaf':
                                    filename = f'{second_node}-commands.txt'
                                    complete_path = os.path.join(pasta, filename)
                        
                            first_line = "table_set_default tunnel_encap_process_sr tdrop"
                            if not contains_line(complete_path, first_line):
                                with open(complete_path, 'a') as arquivo:  # 'a' = append
                                    arquivo.write(first_line)
                            if not contains_line(complete_path, linha):
                                with open(complete_path, 'a') as arquivo:  
                                    arquivo.write('\n' + linha)
                                clean_and_sort_file(complete_path)
                                print('\nInfos adicionadas na tabela.')
                            else:
                                print("Table already contains that line.")

                ################# core nodes #################
                for node in NETWORKX_TOPO.nodes():
                    if NETWORKX_TOPO.nodes[node]['type'] == 'core':
                        node_id = NETWORKX_TOPO.nodes[node]['node_id']
                        hex_node = hex_node_id(node_id)
                        linha = f"set_crc16_parameters calc {hex_node} 0x0 0x0 false false"
                        filename = f'{node}-commands.txt'
                        complete_path = os.path.join(pasta, filename)
                        if not contains_line(complete_path, linha):
                            with open(complete_path, 'w') as arquivo:
                                arquivo.write(linha)

            elif action == 3:
                print("Emptying all tables...")

                pasta = os.path.join(os.getcwd(), "polka", "config")
                if not os.path.exists(pasta):
                    os.makedirs(pasta)

                for node in NETWORKX_TOPO.nodes():
                    if NETWORKX_TOPO.nodes[node]['type'] == 'leaf':
                        filename = f'{node}-commands.txt'
                        complete_path = os.path.join(pasta, filename)
                        with open(complete_path, 'w'):
                            pass
                for node in NETWORKX_TOPO.nodes():
                    if NETWORKX_TOPO.nodes[node]['type'] == 'core':
                        filename = f'{node}-commands.txt'
                        complete_path = os.path.join(pasta, filename)
                        with open(complete_path, 'w'):
                            pass
                print('\nTables emptied.')
            
            elif action == 4:
                CLI(MN_NET)

            elif action == 5:
                debug_menu(NETWORKX_TOPO)

        except Exception as e:
            print(f"Error: {e}")
            break 