#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comandos para gerenciamento de ferramentas MCP.

Este módulo implementa comandos CLI para interagir com as ferramentas MCP,
utilizando o caso de uso MCPToolsUseCase da camada de aplicação.
"""

import os
import sys
import json
import logging
from typing import Optional, Dict, Any, List
from rich import print
from rich.console import Console
from rich.table import Table

from application.use_cases.mcp_tools_use_case import MCPToolsUseCase
from domain.services.mcp_service import MCPService
from infrastructure.mcp_client.mcp_client import MCPClient
from domain.exceptions import ToolNotFoundError, ToolExecutionError

# Configuração de log
logger = logging.getLogger(__name__)
console = Console()


def _criar_caso_uso() -> MCPToolsUseCase:
    """
    Cria e configura a instância do caso de uso MCPToolsUseCase.
    
    Returns:
        MCPToolsUseCase: Instância configurada do caso de uso
    """
    try:
        # Criar cliente MCP
        mcp_client = MCPClient()
        
        # Criar serviço MCP
        mcp_service = MCPService(mcp_client=mcp_client)
        
        # Criar caso de uso
        tools_use_case = MCPToolsUseCase(mcp_service=mcp_service)
        
        return tools_use_case
    except Exception as e:
        logger.error(f"Erro ao criar caso de uso MCPToolsUseCase: {e}")
        raise


def listar_ferramentas() -> None:
    """
    Lista todas as ferramentas disponíveis no MCP, organizadas por categoria.
    """
    try:
        # Obter caso de uso
        tools_use_case = _criar_caso_uso()
        
        print("🔍 Obtendo lista de ferramentas disponíveis...")
        
        # Obter ferramentas organizadas por categoria
        tools_by_category = tools_use_case.list_available_tools()
        
        if not tools_by_category:
            print("ℹ️ Nenhuma ferramenta MCP disponível")
            return
            
        # Exibir ferramentas por categoria
        for category, tools in tools_by_category.items():
            if not tools:
                continue
                
            # Criar tabela para a categoria
            tabela = Table(title=f"🔌 Ferramentas MCP - Categoria: {category}")
            tabela.add_column("ID", style="blue")
            tabela.add_column("Nome", style="cyan")
            tabela.add_column("Descrição", style="green")
            
            # Adicionar ferramentas à tabela
            for tool in tools:
                tabela.add_row(
                    str(tool.get("id", "")),
                    tool.get("name", ""),
                    tool.get("short_description") or tool.get("description", "")
                )
                
            # Exibir tabela
            console.print(tabela)
            console.print("")  # Linha em branco entre categorias
            
    except Exception as e:
        logger.error(f"Erro ao listar ferramentas: {e}")
        print(f"❌ Erro ao listar ferramentas: {e}")


def buscar_ferramentas(texto_busca: str) -> None:
    """
    Busca ferramentas com base em um texto.
    
    Args:
        texto_busca: Texto para buscar em nomes e descrições de ferramentas
    """
    if not texto_busca:
        print("❌ Texto de busca não informado")
        return
        
    try:
        # Obter caso de uso
        tools_use_case = _criar_caso_uso()
        
        print(f"🔍 Buscando ferramentas com texto: '{texto_busca}'...")
        
        # Buscar ferramentas
        ferramentas = tools_use_case.search_tools(texto_busca)
        
        if not ferramentas:
            print(f"ℹ️ Nenhuma ferramenta encontrada para: '{texto_busca}'")
            return
            
        # Criar tabela de resultados
        tabela = Table(title=f"🔌 Ferramentas MCP - Resultados para '{texto_busca}'")
        tabela.add_column("ID", style="blue")
        tabela.add_column("Nome", style="cyan")
        tabela.add_column("Categoria", style="yellow")
        tabela.add_column("Descrição", style="green")
        
        # Adicionar ferramentas à tabela
        for tool in ferramentas:
            tabela.add_row(
                str(tool.get("id", "")),
                tool.get("name", ""),
                tool.get("category", ""),
                tool.get("short_description") or tool.get("description", "")
            )
            
        # Exibir tabela
        console.print(tabela)
        print(f"✅ Encontradas {len(ferramentas)} ferramentas")
        
    except Exception as e:
        logger.error(f"Erro ao buscar ferramentas: {e}")
        print(f"❌ Erro ao buscar ferramentas: {e}")


def mostrar_detalhes_ferramenta(tool_id: str) -> None:
    """
    Mostra detalhes completos de uma ferramenta.
    
    Args:
        tool_id: ID da ferramenta
    """
    if not tool_id:
        print("❌ ID da ferramenta não informado")
        return
        
    try:
        # Obter caso de uso
        tools_use_case = _criar_caso_uso()
        
        print(f"🔍 Obtendo detalhes da ferramenta: '{tool_id}'...")
        
        # Buscar detalhes da ferramenta
        try:
            ferramenta = tools_use_case.get_tool_details(tool_id)
            
            # Exibir detalhes formatados
            print(f"📋 Detalhes da ferramenta:")
            print(f"  ID: {ferramenta.get('id')}")
            print(f"  Nome: {ferramenta.get('name')}")
            print(f"  Categoria: {ferramenta.get('category', 'Não categorizada')}")
            print(f"  Descrição: {ferramenta.get('description')}")
            
            # Exibir parâmetros se existirem
            if ferramenta.get("parameters"):
                print("\n📝 Parâmetros aceitos:")
                for param_name, param_info in ferramenta.get("parameters", {}).items():
                    print(f"  {param_name}: {param_info.get('description', '')}")
                    print(f"    Tipo: {param_info.get('type', 'indefinido')}")
                    if param_info.get("required", False):
                        print(f"    Obrigatório: Sim")
                    
            print("\n✅ Para executar esta ferramenta, use:")
            print(f"  arcee mcp-tools executar {tool_id} --params '{{}}'")
            
        except ToolNotFoundError:
            print(f"❌ Ferramenta não encontrada: {tool_id}")
            
    except Exception as e:
        logger.error(f"Erro ao obter detalhes da ferramenta: {e}")
        print(f"❌ Erro ao obter detalhes da ferramenta: {e}")


def executar_ferramenta(tool_id: str, params_json: Optional[str] = None) -> None:
    """
    Executa uma ferramenta com os parâmetros fornecidos.
    
    Args:
        tool_id: ID da ferramenta
        params_json: Parâmetros em formato JSON (opcional)
    """
    if not tool_id:
        print("❌ ID da ferramenta não informado")
        return
        
    # Processar parâmetros JSON
    params = {}
    if params_json:
        try:
            params = json.loads(params_json)
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao processar parâmetros JSON: {e}")
            print("💡 Os parâmetros devem estar em formato JSON válido")
            return
            
    try:
        # Obter caso de uso
        tools_use_case = _criar_caso_uso()
        
        print(f"🚀 Executando ferramenta: '{tool_id}'...")
        
        # Executar ferramenta
        try:
            resultado = tools_use_case.execute_tool(tool_id, params)
            
            print(f"✅ Ferramenta executada com sucesso:")
            print(json.dumps(resultado.get("result", {}), indent=2, ensure_ascii=False))
            
        except ToolNotFoundError as e:
            print(f"❌ Ferramenta não encontrada: {tool_id}")
        except ToolExecutionError as e:
            print(f"❌ Erro ao executar ferramenta: {e}")
            
    except Exception as e:
        logger.error(f"Erro ao executar ferramenta: {e}")
        print(f"❌ Erro ao executar ferramenta: {e}")


# Funções para o CLI
def main_listar() -> None:
    """Função de comando para listar ferramentas MCP."""
    listar_ferramentas()


def main_buscar(texto_busca: str) -> None:
    """Função de comando para buscar ferramentas MCP."""
    buscar_ferramentas(texto_busca)


def main_detalhes(tool_id: str) -> None:
    """Função de comando para mostrar detalhes de uma ferramenta MCP."""
    mostrar_detalhes_ferramenta(tool_id)


def main_executar(tool_id: str, params_json: Optional[str] = None) -> None:
    """Função de comando para executar uma ferramenta MCP."""
    executar_ferramenta(tool_id, params_json) 