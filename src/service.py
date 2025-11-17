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

# constantes
CURRENT_FILE = os.path.abspath(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_FILE, "..", ".."))

# variáveis globais
debug = False
networx_topo = None
mn_net = None

# Remove qualquer configuração de log pré-existente (feita por outras libs)
root = logging.getLogger()
for handler in root.handlers[:]:
    root.removeHandler(handler)
#################################


def init_net() -> str: 
    global networx_topo, mn_net
    if mn_net == None:
        print("inicializing networkx and mininet,,,")
        pasta = os.path.join(PROJECT_ROOT, "topology")
        gml = get_gml_file(pasta)
        if not gml:
            return "GML file not found."
        networx_topo = loadNXtopology(gml)
        polys = os.path.join(PROJECT_ROOT, "polynomials.txt")
        attribute_node_ids(networx_topo, polys)
        mn_net = loadMininet(networx_topo)
        run_net(mn_net)
        return "Mininet inicialized."
    else:
        return "Mininet is already running."
    

def stop_net() -> str:
    global mn_net
    if mn_net == None:
        return "Mininet is not running."
    mn_net.stop()
    subprocess.run(['sudo', 'mn', '-c']) 
    return "Mininet stopped."


def show_paths(source: str, target: str) -> list[str]:
    global networx_topo
    all_paths = get_all_paths_between_hosts(networx_topo, source, target)
    if not all_paths:
        return ["no paths found."]
    # Numera e formata cada caminho como "0: h1 -> s1 -> s2 -> h2"
    return [f"{i}: {' -> '.join(path)}" for i, path in enumerate(all_paths)]


def config_single_path(index: int, source: str, target: str) -> str:
    global networx_topo, mn_net, debug
    all_paths = get_all_paths_between_hosts(networx_topo, source, target)

    ############### IDA ###############
    chosen_path = all_paths[index]
    
    path_node_ids = get_node_ids(networx_topo, chosen_path)
    port_ids = decimal_to_binary(get_output_ports_list(chosen_path, mn_net, networx_topo))
    routeID = calculate_routeid(path_node_ids, port_ids, debug=debug)
    target_ip = mn_net.get(target).IP()
    output_port = get_leaf_to_core_port_from_path(mn_net, chosen_path, networx_topo)
    target_mac = mn_net.get(target).MAC()
    routeID_int = shifting(routeID)

    linha = f"table_add tunnel_encap_process_sr add_sourcerouting_header {target_ip}/32 => {output_port} {target_mac} {routeID_int}"
    
    second_node = chosen_path[1]
    switch = mn_net.get(second_node)
    partes = linha.split()
    switch.bmv2Thrift(*partes)
    
    ############### VOLTA ###############
    path_volta = chosen_path[::-1]
    path_node_ids = get_node_ids(networx_topo, path_volta)
    port_ids = decimal_to_binary(get_output_ports_list(path_volta, mn_net, networx_topo))
    routeID = calculate_routeid(path_node_ids, port_ids, debug=debug)
    target_ip = mn_net.get(source).IP()
    output_port = get_leaf_to_core_port_from_path(mn_net, path_volta, networx_topo)
    target_mac = mn_net.get(source).MAC()
    routeID_int = shifting(routeID)

    linha = f"table_add tunnel_encap_process_sr add_sourcerouting_header {target_ip}/32 => {output_port} {target_mac} {routeID_int}"

    second_node = path_volta[1]
    switch = mn_net.get(second_node)
    partes = linha.split()
    switch.bmv2Thrift(*partes)

    return f"Path between {source} and {target} configured."


def config_shortest_paths() -> str:
    global networx_topo, mn_net, debug
    hosts = mn_net.hosts 

    ##################### CONFIG SWITCHES #####################
    for i in range(len(hosts)):
        source = hosts[i].name
        for j in range(len(hosts)):
            target = hosts[j].name

            if source == target:
                continue

            try:
                path = networkx.shortest_path(networx_topo, source, target)
            except Exception as e:
                print(f"Error: {e}")
                break  

            ############ IDA ############
            path_node_ids = get_node_ids(networx_topo, path)
            port_ids = decimal_to_binary(get_output_ports_list(path, mn_net, networx_topo))
            routeID = calculate_routeid(path_node_ids, port_ids, debug=debug)
            routeID_int = shifting(routeID)
            output_port = get_leaf_to_core_port_from_path(mn_net, path, networx_topo)

            target_ip = mn_net.get(target).IP()
            target_mac = mn_net.get(target).MAC()

            linha = f"table_add tunnel_encap_process_sr add_sourcerouting_header {target_ip}/32 => {output_port} {target_mac} {routeID_int}"
            partes = linha.split()

            second_node = path[1]
            if networx_topo.nodes[second_node].get('type') == 'leaf':
                switch = mn_net.get(second_node)
                # configura o switch
                switch.bmv2Thrift(*partes) # passa cada parte como um parametro

    return "Shortest path between hosts configured."


# def run_command(command: str):
