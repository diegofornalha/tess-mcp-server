#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Serviço de domínio para operações MCP.

Este módulo implementa o serviço de domínio para operações relacionadas ao MCP,
como gerenciamento de ferramentas, execução de comandos e processamento de dados.
"""

import logging
from typing import Dict, List, Any, Optional

from domain.interfaces.mcp_client import MCPClientInterface
from domain.exceptions import ToolNotFoundError, ToolExecutionError

logger = logging.getLogger(__name__)


class MCPService:
    """
    Serviço de domínio para operações MCP.
    
    Esta classe encapsula a lógica de negócio relacionada às operações MCP,
    utilizando o cliente MCP para interação com a API.
    """
    
    def __init__(self, mcp_client: MCPClientInterface):
        """
        Inicializa o serviço com um cliente MCP.
        
        Args:
            mcp_client: Cliente MCP que implementa a interface MCPClientInterface
        """
        self.mcp_client = mcp_client
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        Lista todas as ferramentas disponíveis no MCP.
        
        Returns:
            Lista de ferramentas disponíveis
        """
        try:
            return self.mcp_client.list_tools()
        except Exception as e:
            logger.error(f"Erro ao listar ferramentas: {str(e)}")
            raise
    
    def get_tool_details(self, tool_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes de uma ferramenta específica.
        
        Args:
            tool_id: ID da ferramenta
            
        Returns:
            Detalhes da ferramenta
            
        Raises:
            ToolNotFoundError: Se a ferramenta não for encontrada
        """
        try:
            tool = self.mcp_client.get_tool(tool_id)
            if not tool:
                raise ToolNotFoundError(f"Ferramenta não encontrada: {tool_id}")
            return tool
        except Exception as e:
            if isinstance(e, ToolNotFoundError):
                raise
            logger.error(f"Erro ao obter detalhes da ferramenta {tool_id}: {str(e)}")
            raise ToolNotFoundError(f"Falha ao obter detalhes da ferramenta: {str(e)}")
    
    def execute_tool(self, tool_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa uma ferramenta com os parâmetros fornecidos.
        
        Args:
            tool_id: ID da ferramenta a ser executada
            parameters: Parâmetros para execução da ferramenta (opcional)
            
        Returns:
            Resultado da execução da ferramenta
            
        Raises:
            ToolNotFoundError: Se a ferramenta não for encontrada
            ToolExecutionError: Se houver falha na execução da ferramenta
        """
        try:
            # Verifica se a ferramenta existe
            tool = self.get_tool_details(tool_id)
            
            # Executa a ferramenta
            if parameters is None:
                parameters = {}
                
            result = self.mcp_client.execute_tool(tool_id, parameters)
            return result
        except ToolNotFoundError:
            logger.error(f"Ferramenta não encontrada para execução: {tool_id}")
            raise
        except Exception as e:
            logger.error(f"Erro ao executar ferramenta {tool_id}: {str(e)}")
            raise ToolExecutionError(f"Falha ao executar ferramenta: {str(e)}")
    
    def get_tool_categories(self) -> List[str]:
        """
        Obtém todas as categorias de ferramentas disponíveis.
        
        Returns:
            Lista de categorias de ferramentas
        """
        try:
            tools = self.list_tools()
            categories = set()
            
            for tool in tools:
                category = tool.get("category")
                if category:
                    categories.add(category)
            
            return sorted(list(categories))
        except Exception as e:
            logger.error(f"Erro ao obter categorias de ferramentas: {str(e)}")
            raise
    
    def get_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Obtém todas as ferramentas de uma categoria específica.
        
        Args:
            category: Nome da categoria
            
        Returns:
            Lista de ferramentas da categoria especificada
        """
        try:
            tools = self.list_tools()
            return [
                tool for tool in tools
                if tool.get("category") == category
            ]
        except Exception as e:
            logger.error(f"Erro ao obter ferramentas da categoria {category}: {str(e)}")
            raise
    
    def find_tool_by_name(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Busca uma ferramenta pelo nome.
        
        Args:
            tool_name: Nome da ferramenta
            
        Returns:
            Detalhes da ferramenta se encontrada, None caso contrário
        """
        try:
            tools = self.list_tools()
            
            # Busca exata
            for tool in tools:
                if tool.get("name") == tool_name:
                    return tool
            
            # Busca por correspondência parcial
            for tool in tools:
                if tool_name.lower() in tool.get("name", "").lower():
                    return tool
            
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar ferramenta por nome {tool_name}: {str(e)}")
            raise 