#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface para o cliente MCP.

Este módulo define a interface para o cliente MCP (Model Context Protocol),
que é responsável pela comunicação com APIs que implementam o protocolo MCP.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple


class MCPClientInterface(ABC):
    """
    Interface para o cliente MCP.
    
    Esta interface define os métodos que um cliente MCP deve implementar
    para comunicação com APIs que seguem o Model Context Protocol.
    """
    
    @abstractmethod
    def health_check(self) -> Tuple[bool, str]:
        """
        Verifica a saúde da conexão com o MCP.
        
        Returns:
            Tupla contendo o status (True se saudável) e uma mensagem descritiva
        """
        pass
    
    @abstractmethod
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        Lista todas as ferramentas disponíveis no MCP.
        
        Returns:
            Lista de ferramentas disponíveis
        """
        pass
    
    @abstractmethod
    def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém os detalhes de uma ferramenta específica pelo ID.
        
        Args:
            tool_id: ID da ferramenta
            
        Returns:
            Detalhes da ferramenta ou None se não encontrada
        """
        pass
    
    @abstractmethod
    def execute_tool(self, tool_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa uma ferramenta com os parâmetros fornecidos.
        
        Args:
            tool_id: ID da ferramenta a ser executada
            parameters: Parâmetros para execução da ferramenta (opcional)
            
        Returns:
            Resultado da execução da ferramenta
        """
        pass
    
    @abstractmethod
    def get_mcp_session_id(self) -> Optional[str]:
        """
        Obtém o ID da sessão MCP atual.
        
        Returns:
            ID da sessão ou None se não estiver configurado
        """
        pass
    
    @abstractmethod
    def save_mcp_session_id(self, session_id: str) -> None:
        """
        Salva o ID da sessão MCP.
        
        Args:
            session_id: ID da sessão a ser salvo
        """
        pass
    
    @abstractmethod
    def check_mcp_configured(self) -> bool:
        """
        Verifica se o cliente MCP está configurado corretamente.
        
        Returns:
            True se configurado, False caso contrário
        """
        pass
    
    @abstractmethod
    def clear_mcp_config(self) -> None:
        """
        Limpa a configuração do cliente MCP.
        """
        pass
    
    @abstractmethod
    def get_mcp_config(self) -> Dict[str, Any]:
        """
        Obtém a configuração atual do cliente MCP.
        
        Returns:
            Configuração atual do cliente MCP
        """
        pass
    
    @abstractmethod
    def save_mcp_config(self, config: Dict[str, Any]) -> None:
        """
        Salva a configuração do cliente MCP.
        
        Args:
            config: Configuração a ser salva
        """
        pass 