#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cliente MCP que implementa a interface definida no domínio.

Este módulo implementa o cliente para comunicação com a API do MCP (Model Context Protocol),
permitindo o acesso a ferramentas, execução de comandos e outras funcionalidades.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple

from domain.interfaces.mcp_client import MCPClientInterface
from infrastructure.providers.mcp_provider import MCPProvider

logger = logging.getLogger(__name__)


class MCPClient(MCPClientInterface):
    """
    Cliente para comunicação com a API do MCP.
    
    Esta classe implementa a interface MCPClientInterface e utiliza o MCPProvider
    para gerenciar a sessão e realizar requisições à API do MCP.
    """
    
    def __init__(self, mcp_provider: MCPProvider = None):
        """
        Inicializa o cliente MCP.
        
        Args:
            mcp_provider: Provider MCP para gerenciamento da sessão (opcional)
        """
        self.mcp_provider = mcp_provider or MCPProvider()
        self._tools_cache = None
    
    def health_check(self) -> Tuple[bool, str]:
        """
        Verifica a saúde da conexão com o MCP.
        
        Returns:
            Tupla contendo o status (True se saudável) e uma mensagem descritiva
        """
        try:
            session_id = self.get_mcp_session_id()
            if not session_id:
                return False, "Sessão MCP não configurada"
            
            # Verifica se consegue listar ferramentas como teste básico
            self.list_tools(force_refresh=True)
            return True, "Conexão com MCP está funcionando"
        except Exception as e:
            logger.error(f"Falha na verificação de saúde do MCP: {str(e)}")
            return False, f"Falha na conexão com MCP: {str(e)}"
    
    def list_tools(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Lista todas as ferramentas disponíveis no MCP.
        
        Args:
            force_refresh: Se True, força atualização do cache
            
        Returns:
            Lista de ferramentas disponíveis
        """
        if self._tools_cache is None or force_refresh:
            try:
                session_id = self.get_mcp_session_id()
                if not session_id:
                    raise ValueError("Sessão MCP não configurada")
                
                # Implementar chamada à API do MCP para listar ferramentas
                # Por enquanto, retorna uma lista fictícia para ilustração
                response = {
                    "tools": [
                        {
                            "id": "tool1",
                            "name": "Ferramenta 1",
                            "description": "Descrição da ferramenta 1",
                            "category": "análise"
                        },
                        {
                            "id": "tool2",
                            "name": "Ferramenta 2",
                            "description": "Descrição da ferramenta 2",
                            "category": "processamento"
                        }
                    ]
                }
                
                self._tools_cache = response.get("tools", [])
            except Exception as e:
                logger.error(f"Erro ao listar ferramentas MCP: {str(e)}")
                raise
        
        return self._tools_cache
    
    def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém os detalhes de uma ferramenta específica pelo ID.
        
        Args:
            tool_id: ID da ferramenta
            
        Returns:
            Detalhes da ferramenta ou None se não encontrada
        """
        try:
            tools = self.list_tools()
            
            for tool in tools:
                if tool.get("id") == tool_id:
                    return tool
            
            return None
        except Exception as e:
            logger.error(f"Erro ao obter ferramenta {tool_id}: {str(e)}")
            raise
    
    def execute_tool(self, tool_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa uma ferramenta com os parâmetros fornecidos.
        
        Args:
            tool_id: ID da ferramenta a ser executada
            parameters: Parâmetros para execução da ferramenta (opcional)
            
        Returns:
            Resultado da execução da ferramenta
        """
        try:
            session_id = self.get_mcp_session_id()
            if not session_id:
                raise ValueError("Sessão MCP não configurada")
            
            if parameters is None:
                parameters = {}
            
            # Verificar se a ferramenta existe
            tool = self.get_tool(tool_id)
            if not tool:
                raise ValueError(f"Ferramenta não encontrada: {tool_id}")
            
            # Implementar chamada à API do MCP para executar a ferramenta
            # Por enquanto, retorna um resultado fictício para ilustração
            result = {
                "status": "success",
                "tool_id": tool_id,
                "result": f"Resultado da execução da ferramenta {tool.get('name')}"
            }
            
            return result
        except Exception as e:
            logger.error(f"Erro ao executar ferramenta {tool_id}: {str(e)}")
            raise
    
    def get_mcp_session_id(self) -> Optional[str]:
        """
        Obtém o ID da sessão MCP atual.
        
        Returns:
            ID da sessão ou None se não estiver configurado
        """
        return self.mcp_provider.get_mcp_session_id()
    
    def save_mcp_session_id(self, session_id: str) -> None:
        """
        Salva o ID da sessão MCP.
        
        Args:
            session_id: ID da sessão a ser salvo
        """
        self.mcp_provider.save_mcp_session_id(session_id)
        # Limpa o cache de ferramentas ao alterar a sessão
        self._tools_cache = None
    
    def check_mcp_configured(self) -> bool:
        """
        Verifica se o MCP está configurado.
        
        Returns:
            True se configurado, False caso contrário
        """
        return self.mcp_provider.check_mcp_configured()
    
    def clear_mcp_config(self) -> None:
        """
        Limpa a configuração do MCP.
        """
        self.mcp_provider.clear_mcp_config()
        self._tools_cache = None
    
    def get_mcp_config(self) -> Dict[str, Any]:
        """
        Obtém a configuração atual do MCP.
        
        Returns:
            Configuração atual do MCP
        """
        return self.mcp_provider.get_mcp_config()
    
    def save_mcp_config(self, config: Dict[str, Any]) -> None:
        """
        Salva a configuração do MCP.
        
        Args:
            config: Configuração a ser salva
        """
        self.mcp_provider.save_mcp_config(config)
        self._tools_cache = None 