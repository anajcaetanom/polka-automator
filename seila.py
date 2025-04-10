import networkx
import matplotlib.pyplot as plt

def loadTopology():
    file = 'topology.gml'
    topology = networkx.read_gml(file, label='label')
    networkx.draw(topology, with_labels=True)
    plt.show()

def main():
    loadTopology()

if __name__ == "__main__":
    main()