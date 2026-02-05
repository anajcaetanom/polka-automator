import time
from client import PolkaAutomatorServiceStub

def testar():
    print("testandorr.......")

    client = PolkaAutomatorServiceStub()

    print("\n----------initnet----------")
    resp = client.init_net()
    print(resp.success)
    print(resp.message)

    time.sleep(2)

    if resp.success:
        print("\n----------show_paths----------")
        resp = client.show_paths("h1", "h2")
        print(resp.success)
        print(resp.paths)
        print(resp.message)

        print("\n----------config_shortest_paths----------")
        resp = client.config_shortest_paths
        print(resp.success)
        print(resp.message)

        print("\n----------stop_net----------")
        resp = client.stop_net
        print(resp.success)
        print(resp.message)

    client.close()

if __name__ == "__main__":
    testar()