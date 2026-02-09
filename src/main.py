import logging
import os
import subprocess

from functools import partial

from load_topology import loadNXtopology, loadMininet
from run_topology import run_net
from utils.user_interface import choose_topo_menu, menu1
from utils.network_utils import attribute_node_ids
from functions import (
    config_single_path,
    config_shortest_path,
    empty_all_tables,
    start_mininet_CLI,
    ping_all_paths
)

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

    MN_NET = loadMininet(NETWORKX_TOPO)
    print("\nStarting mininet...")
    run_net(MN_NET) 

    menu_actions = {
        1: partial(config_single_path, project_root, NETWORKX_TOPO, MN_NET, DEBUG),
        2: partial(config_shortest_path, NETWORKX_TOPO, MN_NET, DEBUG),
        3: partial(empty_all_tables, project_root, NETWORKX_TOPO),
        4: partial(start_mininet_CLI, MN_NET),
        5: partial(ping_all_paths, project_root, MN_NET)
    }

    while True:
        try:
            action = menu1()

            if action == 0:
                print('Stopping and cleaning mininet...')
                MN_NET.stop()
                subprocess.run(['sudo', 'mn', '-c']) 
                print("Exiting...")
                break
            
            menu_actions[action]()

        except Exception as e:
            print(f"Error: {e}")
            break 