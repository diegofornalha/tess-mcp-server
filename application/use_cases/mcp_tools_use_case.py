#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Caso de uso para gerenciamento de ferramentas MCP.

Este módulo implementa o caso de uso para listar, buscar, executar e obter detalhes
de ferramentas disponíveis na plataforma MCP.
"""

import logging
from typing import Dict, List, Any, Optional, Union

from domain.services.mcp_service import MCPService
from domain.exceptions import ToolExecutionError, ToolNotFoundError

logger = logging.getLogger(__name__)


class MCPToolsUseCase:
    """
    Caso de uso para gerenciamento de ferramentas MCP.
    
    Esta classe implementa os casos de uso relacionados às ferramentas disponíveis
    na plataforma MCP, como listar, buscar, executar e obter detalhes.
    """
    
    def __init__(self, mcp_service: MCPService):
        """
        Inicializa o caso de uso com o serviço MCP.
        
        Args:
            mcp_service: Serviço de domínio para operações MCP
        """
        self.mcp_service = mcp_service
    
    def list_available_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Lista todas as ferramentas disponíveis, organizadas por categoria.
        
        Returns:
            Um dicionário com categorias como chaves e listas de ferramentas como valores.
            Inclui uma categoria "uncategorized" para ferramentas sem categoria definida.
        """
        try:
            all_tools = self.mcp_service.list_tools()
            
            # Organizar por categoria
            tools_by_category = {}
            
            for tool in all_tools:
                category = tool.get("category", "uncategorized")
                if category not in tools_by_category:
                    tools_by_category[category] = []
                
                tools_by_category[category].append({
                    "id": tool.get("id"),
                    "name": tool.get("name"),
                    "description": tool.get("description"),
                    "short_description": tool.get("short_description")
                })
            
            return tools_by_category
        except Exception as e:
            logger.error(f"Erro ao listar ferramentas: {str(e)}")
            raise
    
    def search_tools(self, search_text: str) -> List[Dict[str, Any]]:
        """
        Busca ferramentas com base em um texto.
        
        Args:
            search_text: Texto para buscar em nomes e descrições de ferramentas
            
        Returns:
            Lista de ferramentas que correspondem à busca
        """
        try:
            all_tools = self.mcp_service.list_tools()
            search_text = search_text.lower()
            
            matching_tools = []
            for tool in all_tools:
                name = tool.get("name", "").lower()
                description = tool.get("description", "").lower()
                short_description = tool.get("short_description", "").lower()
                
                if (search_text in name or 
                    search_text in description or 
                    search_text in short_description):
                    matching_tools.append({
                        "id": tool.get("id"),
                        "name": tool.get("name"),
                        "category": tool.get("category", "uncategorized"),
                        "description": tool.get("description"),
                        "short_description": tool.get("short_description")
                    })
            
            return matching_tools
        except Exception as e:
            logger.error(f"Erro ao buscar ferramentas: {str(e)}")
            raise
    
    def execute_tool(self, tool_id: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa uma ferramenta específica com os parâmetros fornecidos.
        
        Args:
            tool_id: ID da ferramenta a ser executada
            parameters: Parâmetros para execução da ferramenta (opcional)
            
        Returns:
            Resultado da execução da ferramenta
            
        Raises:
            ToolExecutionError: Se houver falha na execução da ferramenta
            ToolNotFoundError: Se a ferramenta não for encontrada
        """
        try:
            if parameters is None:
                parameters = {}
            
            result = self.mcp_service.execute_tool(tool_id, parameters)
            
            # Formatar o resultado para retorno
            formatted_result = {
                "success": True,
                "tool_id": tool_id,
                "result": result,
                "message": "Ferramenta executada com sucesso"
            }
            
            return formatted_result
        except ToolNotFoundError as e:
            logger.error(f"Ferramenta não encontrada: {str(e)}")
            raise
        except ToolExecutionError as e:
            logger.error(f"Erro ao executar ferramenta: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao executar ferramenta: {str(e)}")
            raise ToolExecutionError(f"Falha ao executar ferramenta {tool_id}: {str(e)}")
    
    def get_tool_details(self, tool_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes completos de uma ferramenta específica.
        
        Args:
            tool_id: ID da ferramenta
            
        Returns:
            Detalhes completos da ferramenta
            
        Raises:
            ToolNotFoundError: Se a ferramenta não for encontrada
        """
        try:
            return self.mcp_service.get_tool_details(tool_id)
        except ToolNotFoundError:
            logger.error(f"Ferramenta não encontrada: {tool_id}")
            raise
        except Exception as e:
            logger.error(f"Erro ao obter detalhes da ferramenta: {str(e)}")
            raise ToolNotFoundError(f"Falha ao obter detalhes da ferramenta {tool_id}: {str(e)}") 