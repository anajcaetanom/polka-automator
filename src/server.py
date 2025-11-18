import logging
import grpc
from concurrent import futures
import network_pb2
import network_pb2_grpc

# Importa suas funções originais
from service import (
    init_net,
    stop_net,
    show_paths,
    config_single_path,
    config_shortest_paths,
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PolkaAutomatorServiceServicer(network_pb2_grpc.PolkaAutomatorServiceServicer):
    """Implementação do serviço gRPC"""
    
    def InitNet(self, request, context):
        """Inicializa a rede Mininet"""
        try:
            logger.info("Chamada InitNet recebida")
            message = init_net()
            success = "already running" in message.lower() or "inicialized" in message.lower()
            
            return network_pb2.Response(
                success=success,
                message=message
            )
        except Exception as e:
            logger.error(f"Erro em InitNet: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return network_pb2.Response(
                success=False,
                message=f"Erro: {str(e)}"
            )
    
    def StopNet(self, request, context):
        """Para a rede Mininet"""
        try:
            logger.info("Chamada StopNet recebida")
            message = stop_net()
            success = "stopped" in message.lower()
            
            return network_pb2.Response(
                success=success,
                message=message
            )
        except Exception as e:
            logger.error(f"Erro em StopNet: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return network_pb2.Response(
                success=False,
                message=f"Erro: {str(e)}"
            )
    
    def ShowPaths(self, request, context):
        """Mostra todos os caminhos entre source e target"""
        try:
            logger.info(f"Chamada ShowPaths recebida: {request.source} -> {request.target}")
            
            if not request.source or not request.target:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Source e target são obrigatórios")
                return network_pb2.PathsResponse(
                    success=False,
                    paths=[],
                    message="Source e target são obrigatórios"
                )
            
            paths = show_paths(request.source, request.target)
            
            if paths and paths[0] == "no paths found.":
                return network_pb2.PathsResponse(
                    success=False,
                    paths=[],
                    message="Nenhum caminho encontrado"
                )
            
            return network_pb2.PathsResponse(
                success=True,
                paths=paths,
                message=f"{len(paths)} caminhos encontrados"
            )
        except Exception as e:
            logger.error(f"Erro em ShowPaths: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return network_pb2.PathsResponse(
                success=False,
                paths=[],
                message=f"Erro: {str(e)}"
            )
    
    def ConfigSinglePath(self, request, context):
        """Configura um caminho específico"""
        try:
            logger.info(f"Chamada ConfigSinglePath recebida: index={request.index}, {request.source} -> {request.target}")
            
            if not request.source or not request.target:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Source e target são obrigatórios")
                return network_pb2.Response(
                    success=False,
                    message="Source e target são obrigatórios"
                )
            
            if request.index < 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Index deve ser maior ou igual a 0")
                return network_pb2.Response(
                    success=False,
                    message="Index deve ser maior ou igual a 0"
                )
            
            message = config_single_path(request.index, request.source, request.target)
            success = "configured" in message.lower()
            
            return network_pb2.Response(
                success=success,
                message=message
            )
        except IndexError:
            logger.error(f"Index {request.index} fora dos limites")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Index de caminho inválido")
            return network_pb2.Response(
                success=False,
                message="Index de caminho inválido"
            )
        except Exception as e:
            logger.error(f"Erro em ConfigSinglePath: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return network_pb2.Response(
                success=False,
                message=f"Erro: {str(e)}"
            )
    
    def ConfigShortestPaths(self, request, context):
        """Configura os caminhos mais curtos"""
        try:
            logger.info("Chamada ConfigShortestPaths recebida")
            message = config_shortest_paths()
            success = "configured" in message.lower()
            
            return network_pb2.Response(
                success=success,
                message=message
            )
        except Exception as e:
            logger.error(f"Erro em ConfigShortestPaths: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return network_pb2.Response(
                success=False,
                message=f"Erro: {str(e)}"
            )


def serve(port=50051, max_workers=10):
    """Inicia o servidor gRPC"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    network_pb2_grpc.add_PolkaAutomatorServiceServicer_to_server(
        PolkaAutomatorServiceServicer(), server
    )
    
    server_address = f'[::]:{port}'
    server.add_insecure_port(server_address)
    
    logger.info(f"Servidor gRPC iniciando em {server_address}")
    server.start()
    logger.info("Servidor gRPC rodando...")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Encerrando servidor...")
        server.stop(0)


if __name__ == '__main__':
    serve()