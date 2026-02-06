import logging
import os
import subprocess

from load_topology import loadNXtopology, loadMininet
from run_topology import run_net
from utils.user_interface import choose_topo_menu, menu1
from utils.network_utils import attribute_node_ids
from functions import *

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
        1: config_single_path,
        2: config_shortest_path,
        3: empty_all_tables,
        4: start_mininet_CLI,
        5: ping_all_paths
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
            
            menu_actions[action](project_root, NETWORKX_TOPO, MN_NET, DEBUG)

        except Exception as e:
            print(f"Error: {e}")
            break 