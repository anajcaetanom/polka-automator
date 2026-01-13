import grpc
import service_pb2
import service_pb2_grpc
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class PolkaAutomatorServiceStub:
    """Cliente gRPC para interagir com o NetworkService"""
    
    def __init__(self, host='localhost', port=50051):
        """
        Inicializa o cliente
        
        Args:
            host: Endereço do servidor
            port: Porta do servidor
        """
        self.address = f'{host}:{port}'
        self.channel = grpc.insecure_channel(self.address)
        self.stub = network_pb2_grpc.NetworkServiceStub(self.channel)
        logger.info(f"✓ Cliente conectado a {self.address}\n")
    
    def init_net(self):
        """Inicializa a rede Mininet"""
        try:
            response = self.stub.StartNetwork(network_pb2.Empty())
            return response
        except grpc.RpcError as e:
            logger.error(f"Erro RPC: {e.code()} - {e.details()}")
            return None
    
    def stop_net(self):
        """Para a rede Mininet"""
        try:
            response = self.stub.StopNetwork(network_pb2.Empty())
            return response
        except grpc.RpcError as e:
            logger.error(f"Erro RPC: {e.code()} - {e.details()}")
            return None
    
    def show_paths(self, source, target):
        """Mostra todos os caminhos entre source e target"""
        try:
            request = network_pb2.PathRequest(source=source, target=target)
            response = self.stub.ShowPaths(request)
            return response
        except grpc.RpcError as e:
            logger.error(f"Erro RPC: {e.code()} - {e.details()}")
            return None
    
    def config_single_path(self, index, source, target):
        """Configura um caminho específico"""
        try:
            request = network_pb2.SinglePathRequest(
                index=index,
                source=source,
                target=target
            )
            response = self.stub.ConfigSinglePath(request)
            return response
        except grpc.RpcError as e:
            logger.error(f"Erro RPC: {e.code()} - {e.details()}")
            return None
    
    def config_shortest_paths(self):
        """Configura os caminhos mais curtos"""
        try:
            response = self.stub.ConfigShortestPaths(network_pb2.Empty())
            return response
        except grpc.RpcError as e:
            logger.error(f"Erro RPC: {e.code()} - {e.details()}")
            return None
    
    def close(self):
        """Fecha a conexão com o servidor"""
        self.channel.close()
        logger.info("\n✓ Conexão fechada")
