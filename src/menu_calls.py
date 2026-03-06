import os
import networkx

from mininet.cli import CLI
from polka.tools import calculate_routeid, shifting

from utils.file_utils import contains_line, clean_and_sort_file
from utils.user_interface import get_host, menu2
from utils.network_utils import (
    get_all_paths_between_hosts,
    hex_node_id,
    get_node_ids,
    get_node_number,
    decimal_to_binary,
    get_output_ports_list,
    get_leaf_to_core_port_from_path,
)


def config_single_path(pasta, NETWORKX_TOPO, MN_NET, DEBUG) -> None:
    source = get_host("\nType the source host (ex: h1): ")
    target = get_host("Type the target host (ex: h2): ")

    # print all paths between source and target and let the user choose one.
    all_paths = get_all_paths_between_hosts(NETWORKX_TOPO, source, target)
    
    print(f"\nFound {len(all_paths)} paths between {source} and {target}:\n")

    ############### IDA ###############
    chosen_path = menu2(all_paths)
    if chosen_path == 0:
        return
    
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
        partes = linha.split()
        switch = MN_NET.get(second_node)
        switch.bmv2Thrift(*partes)

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
        partes = linha.split()
        switch = MN_NET.get(second_node)
        switch.bmv2Thrift(*partes)

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

    print("\nPath configured.\n")

def config_shortest_path(NETWORKX_TOPO, MN_NET, DEBUG) -> None:
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
                return -1  

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

    print("Shortest path between hosts configured.")

def empty_all_tables(project_root, NETWORKX_TOPO) -> None:
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

def start_mininet_CLI(MN_NET):
    print("\nStarting CLI...")
    CLI(MN_NET)

def ping_all_paths(project_root, MN_NET):
    pasta = os.path.join(project_root, "polka", "config")
    if not os.path.exists(pasta):
        print("pasta config não existe.")
        return

    hosts = MN_NET.hosts

    for i in range(len(hosts)):
        source = hosts[i].name

        switch = MN_NET.get(source)
        filename = f'{source}-commands.txt'
        complete_path = os.path.join(pasta, filename)
        with open(complete_path, 'r') as arquivo:
            next(arquivo) # pula a primeira linha
            for linha in arquivo:
                partes = linha.split()
                switch.bmv2Thrift(*partes) # passa cada parte como um parametro 
                ip_com_mascara = partes[3]
                ip_partes = ip_com_mascara.split("/")
                ip_destino = ip_partes[0]
                route_id = partes[-1]
                print(f'\nPing {source} to {ip_destino}. RouteID: {route_id}')
                print(hosts[i].cmd(f'ping -c 1 {ip_destino}'))