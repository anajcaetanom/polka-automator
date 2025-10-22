import ipaddress
import os

def contains_line(filename, target_line):
    """
    Checks if a file contains a specific line.
    """
    try:
        with open(filename, 'r') as file:
            return any(line.strip() == target_line for line in file)
    except FileNotFoundError:
        print(f"[Error] File not found: {filename}")
        return False
    except Exception as e:
        print(f"[Error] while checking line in file: {e}")
        return False

def clean_and_sort_file(caminho_arquivo):
    """
    Removes empty lines and sorts the remaining ones based on IP addresses.
    """
    try:
        with open(caminho_arquivo, 'r') as f:
            linhas = f.readlines()
        if not linhas:
            return  # arquivo vazio, nada a fazer

        primeira_linha = linhas[0].rstrip('\n')

        def extract_ip(linha):
            partes = linha.split()
            for parte in partes:
                if '/' in parte:
                    try:
                        return ipaddress.ip_network(parte, strict=False)
                    except ValueError:
                        continue
            return ipaddress.ip_network("255.255.255.255/32") # fallback

        resto_linhas = [linha.strip() for linha in linhas[1:] if linha.strip() != '']
        resto_linhas.sort(key=extract_ip)
        linhas_final = [primeira_linha] + resto_linhas

        with open(caminho_arquivo, 'w') as f:
            for linha in linhas_final:
                f.write(linha + '\n')
    
    except Exception as e:
        print(f"[Error] while cleaning and sorting file: {e}")

def get_gml_file(pasta="topology"):
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
    topo = os.path.join(pasta, selected)

    return topo