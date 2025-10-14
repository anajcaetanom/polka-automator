import logging
import os
import subprocess
import networkx
import grpc

from utils.user_interface import *
from utils.network_utils import *
from utils.file_utils import *

from mininet.cli import CLI
from polka.tools import calculate_routeid, shifting

DEBUG = False


# Remove qualquer configuração de log pré-existente (feita por outras libs)
root = logging.getLogger()
for handler in root.handlers[:]:
    root.removeHandler(handler)
####################

current_file = os.path.abspath(__file__)
project_root = os.path.abspath(os.path.join(current_file, "..", ".."))

pasta_topo = os.path.join(project_root, "topologies")


def show_paths(source, target, NETWORKX_TOPO):
    all_paths = get_all_paths_between_hosts(NETWORKX_TOPO, source, target)

    if not all_paths:
        return [], "no paths found."

    # Numera e formata cada caminho como "0: h1 -> s1 -> s2 -> h2"
    return [f"{i}: {' -> '.join(path)}" for i, path in enumerate(all_paths)]


def config_single_path(index, source, target, NETWORKX_TOPO, MN_NET):

    all_paths = get_all_paths_between_hosts(NETWORKX_TOPO, source, target)

    ############### IDA ###############
    chosen_path = all_paths[index]
    
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
    path_volta = chosen_path[::-1]
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

    return


def pingall(MN_NET, NETWORKX_TOPO):
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


    ping_outputs = []

    ##################### PING #####################
    for i in range(len(hosts)):
        source = hosts[i].name
        for j in range(len(hosts)):
            target = hosts[j].name
            target_ip = MN_NET.get(target).IP()

            out = hosts[i].cmd(f'ping -c 1 {target_ip}')
            ping_outputs.append(out) 

    return ping_outputs
