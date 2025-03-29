"""
Factory para criação de instâncias de servidores MCP.
"""

from typing import Dict, Any, Optional, List, Type
from domain.interfaces.mcp_server import MCPServerInterface
from infrastructure.mcp_servers.registry import MCPServerRegistry


class MCPServerFactory:
    """
    Factory para criação de instâncias de servidores MCP.
    Implementa o padrão Factory Method para criar instâncias concretas
    de servidores baseados em seu identificador.
    """
    
    @staticmethod
    def create(server_id: str, **config: Any) -> MCPServerInterface:
        """
        Cria uma instância de servidor MCP com base no ID fornecido.
        
        Args:
            server_id (str): Identificador do servidor a ser criado.
            **config: Configurações específicas para o servidor.
            
        Returns:
            MCPServerInterface: Uma instância do servidor MCP selecionado.
            
        Raises:
            ValueError: Se o servidor não for encontrado no registro.
        """
        server_class = MCPServerRegistry.get_server_class(server_id)
        return server_class(**config)
    
    @staticmethod
    def list_available_servers() -> Dict[str, Dict[str, Any]]:
        """
        Lista todos os servidores disponíveis com seus metadados.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dicionário com todos os servidores registrados
                                        e seus metadados.
        """
        return MCPServerRegistry.list_servers()
    
    @staticmethod
    def get_server_metadata(server_id: str) -> Dict[str, Any]:
        """
        Retorna os metadados de um servidor específico.
        
        Args:
            server_id (str): Identificador do servidor.
            
        Returns:
            Dict[str, Any]: Metadados do servidor.
            
        Raises:
            ValueError: Se o servidor não for encontrado no registro.
        """
        return MCPServerRegistry.get_server_metadata(server_id) 