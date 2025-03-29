"""
Interface para servidores MCP (Model Context Protocol).

Define o contrato que qualquer implementação de servidor MCP deve seguir.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class MCPServerInterface(ABC):
    """Interface para servidores MCP."""
    
    @abstractmethod
    def start(self) -> bool:
        """
        Inicia o servidor MCP.
        
        Returns:
            bool: True se o servidor foi iniciado com sucesso, False caso contrário.
        """
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """
        Para o servidor MCP.
        
        Returns:
            bool: True se o servidor foi parado com sucesso, False caso contrário.
        """
        pass
    
    @abstractmethod
    def get_status(self) -> str:
        """
        Retorna o status atual do servidor.
        
        Returns:
            str: O status do servidor (ex: "running", "stopped", "error").
        """
        pass
        
    @abstractmethod
    def get_endpoint(self) -> str:
        """
        Retorna o endpoint principal do servidor.
        
        Returns:
            str: A URL do endpoint principal.
        """
        pass
    
    @abstractmethod
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        Lista todas as ferramentas disponíveis no servidor MCP.
        
        Returns:
            List[Dict[str, Any]]: Lista de ferramentas disponíveis.
        """
        pass
    
    @abstractmethod
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma ferramenta específica no servidor MCP.
        
        Args:
            tool_name: Nome da ferramenta a ser executada.
            params: Parâmetros para a execução da ferramenta.
            
        Returns:
            Dict[str, Any]: Resposta da execução da ferramenta.
        """
        pass
    
    @abstractmethod
    def get_server_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o servidor.
        
        Returns:
            Dict[str, Any]: Informações do servidor (versão, capacidades, etc).
        """
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Verifica a saúde do servidor MCP.
        
        Returns:
            Dict[str, Any]: Informações sobre o estado do servidor.
        """
        pass 