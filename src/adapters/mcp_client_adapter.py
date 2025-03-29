#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adaptador para o cliente MCP.

Este módulo fornece compatibilidade do cliente MCP com código legado,
redirecionando as chamadas para a nova implementação.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Tuple

from infrastructure.mcp_client.mcp_client import MCPClient

logger = logging.getLogger(__name__)


class MCPRunClient:
    """
    Adaptador para o cliente MCP.
    
    Esta classe mantém a interface do MCPRunClient original, mas
    redireciona as chamadas para a nova implementação MCPClient.
    """
    
    def __init__(self, session_id: Optional[str] = None):
        """
        Inicializa o adaptador para o cliente MCP.
        
        Args:
            session_id: ID de sessão MCP (opcional)
        """
        logger.warning(
            "Usando adaptador MCPRunClient (legado). "
            "Para novas implementações, use infrastructure.mcp_client.MCPClient"
        )
        
        try:
            # Criar instância do novo cliente
            self._client = MCPClient()
            
            # Se fornecido session_id, atualizar na instância
            if session_id:
                self._client.save_mcp_session_id(session_id)
        except Exception as e:
            logger.error(f"Erro ao inicializar adaptador MCPRunClient: {e}")
            raise
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de ferramentas disponíveis.
        
        Returns:
            Lista de ferramentas
        """
        try:
            return self._client.list_tools()
        except Exception as e:
            logger.error(f"Erro ao obter ferramentas (adaptador): {e}")
            return []
    
    def run_tool(self, tool_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executa uma ferramenta com os parâmetros fornecidos.
        
        Args:
            tool_name: Nome da ferramenta
            params: Parâmetros da ferramenta (opcional)
            
        Returns:
            Resultado da execução
        """
        try:
            if params is None:
                params = {}
                
            # Compatibilidade: na API legada, usamos o nome
            # Na nova API, usamos o ID. Precisamos fazer a conversão.
            tool_id = self._find_tool_id_by_name(tool_name)
            
            if not tool_id:
                return {
                    "error": f"Ferramenta não encontrada: {tool_name}",
                    "success": False
                }
            
            # Executar a ferramenta com a nova implementação
            result = self._client.execute_tool(tool_id, params)
            
            # Formatar resultado para compatibilidade
            return {
                "success": True,
                "tool": tool_name,
                "result": result,
                "message": "Ferramenta executada com sucesso"
            }
        except Exception as e:
            logger.error(f"Erro ao executar ferramenta {tool_name} (adaptador): {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def _find_tool_id_by_name(self, tool_name: str) -> Optional[str]:
        """
        Encontra o ID de uma ferramenta pelo nome.
        
        Args:
            tool_name: Nome da ferramenta
            
        Returns:
            ID da ferramenta ou None se não encontrada
        """
        try:
            tools = self.get_tools()
            
            for tool in tools:
                if tool.get("name") == tool_name:
                    return tool.get("id")
            
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar ID da ferramenta {tool_name}: {e}")
            return None


def configure_mcprun(session_id: Optional[str] = None) -> Optional[str]:
    """
    Função de compatibilidade para configurar o cliente MCP.
    
    Args:
        session_id: ID de sessão (opcional)
        
    Returns:
        ID de sessão configurado ou None se falhar
    """
    try:
        logger.warning(
            "Usando configure_mcprun (legado). "
            "Para novas implementações, use MCPClient.save_mcp_session_id"
        )
        
        client = MCPClient()
        
        # Se não fornecido, tentar usar o atual
        if not session_id:
            session_id = client.get_mcp_session_id()
            if not session_id:
                return None
        
        # Salvar o ID de sessão
        client.save_mcp_session_id(session_id)
        
        # Verificar se foi configurado corretamente
        if client.check_mcp_configured():
            return session_id
        else:
            return None
    except Exception as e:
        logger.error(f"Erro ao configurar MCP (adaptador): {e}")
        return None 