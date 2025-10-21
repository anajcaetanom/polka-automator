import re
import os

from utils.test_utils import *

def get_host(prompt):
    """
    Gets a valid host input from the user.
    """
    while True:
        try:
            host = input(prompt).strip().lower()
            if re.fullmatch(r"h\d+", host):
                return host
            else:
                print("Invalid input. Please type a valid host like 'h1', 'h2', ...")
        except Exception as e:
            print(f"[Error] while reading input: {e}")

def menu1():
    """
    Main menu selection.
    """
    while True:
        try:
            print("\nMenu:")
            print("1. Configure a single path.")
            print("2. Ping all hosts.")
            print("3. Empty all tables.")
            print("4. Open Mininet CLI.")
            print("0. Exit.")

            action = input("\nSelect an option: ").strip()

            if action in ('0', '1', '2', '3', '4'):
                return int(action)
            else:
                print("Invalid option. Please try again.")
        except Exception as e:
            print(f"[Error] in menu1: {e}")

def menu2(all_paths):
    """
    Allows user to select one of the listed paths.
    """
    try:
        for i, path in enumerate(all_paths, 1):
            print(f"Path {i}: {' -> '.join(path)}")
        
        while True:
            try:
                option = int(input("\nType the number of a path to choose, or 0 to quit: "))
                if (option == 0):
                    print("Exiting...")
                    return 0
                elif (1 <= option <= len(all_paths)):
                    chosen_path = all_paths[option - 1]
                    print(f"You chose path {option}.\n")
                    return chosen_path
                else:
                    print("Invalid option. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"[Error] in menu2: {e}")
        return None
    
def choose_topo_menu(pasta="topology"):
    """
    Automatically selects the first .gml topology file in the given folder.
    """
    if not os.path.isdir(pasta):
        print(f"Directory does not exist.")
        return None

    arquivos = sorted([file for file in os.listdir(pasta) if file.endswith(".gml")])
    if not arquivos:
        print(f"No .gml files available in directory.")
        return None

    selected = arquivos[0]
    print(f"Topology selected automatically: {selected}")
    topo = os.path.join(pasta, selected)

    return topo

def debug_menu(nx_topo):
    """
    Displays an interactive debug menu for inspecting the NetworkX topology.
    """
    while True:
        try:
            print("\n--- Debug Menu ---")
            print("1. Show networkx topology graph.")
            print("2. List networkx topology nodes.")
            print("0. Go back")

            choice = int(input("Select a option: "))

            if choice == 0:
                break
            elif choice == 1:
                show_nx_topo(nx_topo)
            elif choice == 2:
                print_nodes_by_type(nx_topo)
            else: 
                print(f"Invalid option. Try again.")
        except ValueError:
            print("Invalid entry. Type a number.")
        