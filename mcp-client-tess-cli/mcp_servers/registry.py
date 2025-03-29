"""
Sistema de registro para servidores MCP.
Permite registrar, listar e obter diferentes implementações de servidores MCP.
"""

from typing import Dict, Any, Type, Optional
from domain.interfaces.mcp_server import MCPServerInterface


class MCPServerRegistry:
    """
    Registro centralizado para todos os servidores MCP disponíveis.
    Implementa o padrão Registry para gerenciar diferentes implementações.
    """
    _servers: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register(cls, server_id: str, server_class: Type[MCPServerInterface], **metadata: Any) -> None:
        """
        Registra uma implementação de servidor MCP.
        
        Args:
            server_id (str): Identificador único para o servidor.
            server_class (Type[MCPServerInterface]): Classe que implementa a interface MCPServerInterface.
            **metadata: Metadados adicionais sobre o servidor (descrição, versão, etc).
        """
        cls._servers[server_id] = {
            "class": server_class,
            "metadata": metadata
        }
        print(f"Servidor MCP '{server_id}' registrado com sucesso.")
        
    @classmethod
    def get_server_class(cls, server_id: str) -> Type[MCPServerInterface]:
        """
        Retorna a classe de implementação para um servidor específico.
        
        Args:
            server_id (str): Identificador do servidor.
            
        Returns:
            Type[MCPServerInterface]: A classe que implementa a interface MCPServerInterface.
            
        Raises:
            ValueError: Se o servidor não for encontrado no registro.
        """
        server_info = cls._servers.get(server_id)
        if not server_info:
            raise ValueError(f"Servidor MCP '{server_id}' não encontrado no registro.")
        return server_info["class"]
        
    @classmethod
    def list_servers(cls) -> Dict[str, Dict[str, Any]]:
        """
        Lista todos os servidores MCP disponíveis com seus metadados.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dicionário com chaves sendo os IDs dos servidores
                                       e valores sendo seus metadados.
        """
        return {k: v["metadata"] for k, v in cls._servers.items()}
    
    @classmethod
    def get_server_metadata(cls, server_id: str) -> Dict[str, Any]:
        """
        Retorna os metadados de um servidor específico.
        
        Args:
            server_id (str): Identificador do servidor.
            
        Returns:
            Dict[str, Any]: Metadados do servidor.
            
        Raises:
            ValueError: Se o servidor não for encontrado no registro.
        """
        server_info = cls._servers.get(server_id)
        if not server_info:
            raise ValueError(f"Servidor MCP '{server_id}' não encontrado no registro.")
        return server_info["metadata"]
    
    @classmethod
    def unregister(cls, server_id: str) -> None:
        """
        Remove um servidor do registro.
        
        Args:
            server_id (str): Identificador do servidor a ser removido.
            
        Raises:
            ValueError: Se o servidor não for encontrado no registro.
        """
        if server_id not in cls._servers:
            raise ValueError(f"Servidor MCP '{server_id}' não encontrado no registro.")
        del cls._servers[server_id]
        print(f"Servidor MCP '{server_id}' removido do registro.") 