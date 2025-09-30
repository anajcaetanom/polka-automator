import logging
import os
import subprocess
import networkx

from load_topology import loadNXtopology, loadMininet
from run_topology import run_net
from utils.user_interface import *
from utils.network_utils import *
from utils.file_utils import *

from mininet.cli import CLI
from polka.tools import calculate_routeid, shifting

DEBUG = False

if __name__ == "__main__":

    # Remove qualquer configuração de log pré-existente (feita por outras libs)
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    #

    current_file = os.path.abspath(__file__)
    project_root = os.path.abspath(os.path.join(current_file, "..", ".."))

    pasta_topo = os.path.join(project_root, "topologies")
    selected_topo = choose_topo_menu(pasta_topo) 
    NETWORKX_TOPO = loadNXtopology(selected_topo)

    attribute_node_ids(NETWORKX_TOPO, "polynomials.txt")
    
    basic_config_switches(NETWORKX_TOPO, project_root)
    MN_NET = loadMininet(NETWORKX_TOPO)
    print("\nStarting mininet...")
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

                source = get_host("\nType the source host (ex: h1): ")
                target = get_host("Type the target host (ex: h2): ")

                # print all paths between source and target and let the user choose one.
                all_paths = get_all_paths_between_hosts(NETWORKX_TOPO, source, target)
                
                print(f"\nFound {len(all_paths)} paths between {source} and {target}:\n")

                ############### IDA ###############
                chosen_path = menu2(all_paths)
                if chosen_path == 0:
                    continue
                
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
                    switch = MN_NET.get(second_node)
                    partes = linha.split()
                    switch.bmv2Thrift(*partes)
                
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

                second_node = path_volta[1]
                if NETWORKX_TOPO.nodes[second_node].get('type') == 'leaf':
                    switch = MN_NET.get(second_node)
                    partes = linha.split()
                    switch.bmv2Thrift(*partes)

            elif action == 2:
                hosts = MN_NET.hosts 

                ##################### CONFIG SWITCHES #####################
                for i in range(len(hosts)):
                    source = hosts[i].name
                    for j in range(len(hosts)):
                        target = hosts[j].name

                        if source == target:
                            continue

                        try:
                            path = networkx.shortest_path(NETWORKX_TOPO, source, target)
                        except Exception as e:
                            print(f"Error: {e}")
                            break  

                        print(f"source: {source}") 
                        print(f"target: {target}") 
                        print(f"path: {path}") 


                        ############ IDA ############
                        path_node_ids = get_node_ids(NETWORKX_TOPO, path)
                        port_ids = decimal_to_binary(get_output_ports_list(path, MN_NET, NETWORKX_TOPO))
                        routeID = calculate_routeid(path_node_ids, port_ids, debug=DEBUG)
                        routeID_int = shifting(routeID)
                        output_port = get_leaf_to_core_port_from_path(MN_NET, path, NETWORKX_TOPO)

                        target_ip = MN_NET.get(target).IP()
                        target_mac = MN_NET.get(target).MAC()

                        linha = f"table_add tunnel_encap_process_sr add_sourcerouting_header {target_ip}/32 => {output_port} {target_mac} {routeID_int}"
                        partes = linha.split()

                        second_node = path[1]
                        if NETWORKX_TOPO.nodes[second_node].get('type') == 'leaf':
                            switch = MN_NET.get(second_node)
                            # configura o switch
                            switch.bmv2Thrift(*partes) # passa cada parte como um parametro

                ##################### PING #####################
                for i in range(len(hosts)):
                    source = hosts[i].name
                    for j in range(len(hosts)):
                        target = hosts[j].name
                        target_ip = MN_NET.get(target).IP()

                        print(f'\nPing {source} to {target}.')
                        print(hosts[i].cmd(f'ping -c 1 {target_ip}'))

            elif action == 3:
                print("Emptying all tables...")

                pasta = os.path.join(project_root, "polka", "config")
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

                print("\nYou have altered tables. Please reboot the mininet topology.\n")
            
            elif action == 4:
                print("\nStarting CLI...")
                CLI(MN_NET)

        except Exception as e:
            print(f"Error: {e}")
            break