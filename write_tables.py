from _aux import *

if __name__ == '__main__':
    for leaf in leafs:
        node_number = get_node_number(leaf)

        # Se quiser adicionar conteúdo sem apagar o que já existe, use 'a' (append):
            # arquivo = open('nome_do_arquivo.txt', 'a')

        linhas = [
            "table_set_default tunnel_encap_process_sr tdrop",
        ]

        for edge in switches:
            for host in hosts:
                linha = [
                    f"table_add tunnel_encap_process_sr add_sourcerouting_header {destIP} => {output_port} {destMacAdress} {routeId}"
                ]
                linhas.append(linha)

            with open(f'e{node_number}-commands.txt', 'w') as arquivo:
                arquivo.writelines(linhas)