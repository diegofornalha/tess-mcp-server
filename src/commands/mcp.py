#!/usr/bin/env python
"""
Comandos para interação com o MCP (Module Command Processor).

DEPRECATED: Este módulo está obsoleto e será removido em versões futuras. 
Use os novos comandos em 'arcee mcp-tools' em vez disso.
"""

import os
import sys
import json
import logging
import click
from rich import print
from rich.console import Console
from rich.table import Table
from typing import Optional, Dict, Any, List
from ..utils.logging import get_logger
from pathlib import Path

# Configuração de logger
logger = get_logger(__name__)
console = Console()

# Tente importar o adaptador do MCPRunClient
try:
    from ..adapters.mcp_client_adapter import MCPRunClient, configure_mcprun
    MCPRUN_SIMPLE_AVAILABLE = True
    logger.info("Adaptador MCPRunClient disponível")
except ImportError:
    MCPRUN_SIMPLE_AVAILABLE = False
    logger.warning("Adaptador MCPRunClient não disponível")

# Variável global para armazenar o ID da sessão MCP
_mcp_session_id = None


def get_mcp_session_id() -> Optional[str]:
    """Obtém o ID da sessão MCP salvo."""
    global _mcp_session_id
    
    if _mcp_session_id:
        return _mcp_session_id
        
    # Tenta carregar da configuração
    config_file = os.path.expanduser("~/.arcee/config.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                _mcp_session_id = config.get("mcp_session_id")
                if _mcp_session_id:
                    return _mcp_session_id
        except Exception as e:
            logger.error(f"Erro ao carregar ID de sessão MCP: {e}")
    
    return None


def save_mcp_session_id(session_id: str) -> bool:
    """Salva o ID da sessão MCP na configuração."""
    global _mcp_session_id
    _mcp_session_id = session_id
    
    # Cria o diretório .arcee se não existir
    config_dir = os.path.expanduser("~/.arcee")
    config_file = os.path.join(config_dir, "config.json")
    
    try:
        os.makedirs(config_dir, exist_ok=True)
        
        # Carrega configuração existente se houver
        config = {}
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
        
        # Atualiza com o novo ID de sessão
        config["mcp_session_id"] = session_id
        
        # Salva a configuração
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
            
        logger.info(f"ID de sessão MCP salvo: {session_id}")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar ID de sessão MCP: {e}")
        return False


def configurar_mcp(session_id: Optional[str] = None) -> None:
    """Configura o cliente MCP.run com um ID de sessão."""
    print("⚠️  Comando obsoleto: use o novo comando mcp-tools em seu lugar")
    
    if not MCPRUN_SIMPLE_AVAILABLE:
        print("❌ Adaptador MCPRunClient não está disponível")
        return
    
    try:
        print("🔄 Configurando MCP.run...")
        
        # Usar o configure_mcprun para obter um ID de sessão
        new_session_id = configure_mcprun(session_id)
        
        if new_session_id:
            # Salvar o ID de sessão para uso futuro
            if save_mcp_session_id(new_session_id):
                print(f"✅ ID de sessão MCP configurado: {new_session_id}")
                
                # Testar a conexão listando ferramentas
                client = MCPRunClient(session_id=new_session_id)
                tools = client.get_tools()
                print(f"ℹ️ Encontradas {len(tools)} ferramentas disponíveis")
            else:
                print("⚠️ Configuração salva, mas houve erro ao persistir")
                print(f"ID de sessão atual: {new_session_id}")
        else:
            print("❌ Não foi possível configurar o MCP.run")
            print("💡 Verifique os logs para mais detalhes")
    except Exception as e:
        logger.exception(f"Erro ao configurar MCP.run: {e}")
        print(f"❌ Erro ao configurar MCP.run: {e}")


def listar_ferramentas() -> None:
    """Lista as ferramentas disponíveis no MCP."""
    print("⚠️  Comando obsoleto: use 'arcee mcp-tools listar' em seu lugar")
    
    if not MCPRUN_SIMPLE_AVAILABLE:
        print("❌ Adaptador MCPRunClient não está disponível")
        return
    
    session_id = get_mcp_session_id()
    if not session_id:
        print("❌ MCP não configurado. Execute primeiro: arcee mcp configurar")
        return
    
    print("🔍 Obtendo lista de ferramentas disponíveis...")
    try:
        client = MCPRunClient(session_id=session_id)
        tools = client.get_tools()
        
        if not tools:
            print("ℹ️ Nenhuma ferramenta MCP.run disponível")
            return
            
        # Cria a tabela
        tabela = Table(title="🔌 Ferramentas MCP.run")
        tabela.add_column("Nome", style="cyan")
        tabela.add_column("Descrição", style="green")
        
        # Adiciona as ferramentas à tabela
        for tool in tools:
            tabela.add_row(tool["name"], tool["description"])
            
        # Exibe a tabela
        console.print(tabela)
        
    except Exception as e:
        logger.exception(f"Erro ao listar ferramentas MCP: {e}")
        print(f"❌ Erro ao listar ferramentas MCP: {e}")


def executar_ferramenta(nome: str, params_json: Optional[str] = None) -> None:
    """Executa uma ferramenta MCP específica com os parâmetros fornecidos."""
    print(f"⚠️  Comando obsoleto: use 'arcee mcp-tools executar {nome}' em seu lugar")
    
    if not MCPRUN_SIMPLE_AVAILABLE:
        print("❌ Adaptador MCPRunClient não está disponível")
        return
    
    session_id = get_mcp_session_id()
    if not session_id:
        print("❌ MCP não configurado. Execute primeiro: arcee mcp configurar")
        return
    
    # Processa os parâmetros
    try:
        params = {}
        if params_json:
            params = json.loads(params_json)
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON: {e}")
        print(f"❌ Erro nos parâmetros JSON: {e}")
        return
    
    # Executa a ferramenta
    print(f"🚀 Executando ferramenta '{nome}'...")
    try:
        client = MCPRunClient(session_id=session_id)
        result = client.run_tool(nome, params)
        
        if result.get("error"):
            print(f"❌ Erro ao executar ferramenta: {result['error']}")
            if result.get("raw_output"):
                print("Saída original:")
                print(result["raw_output"])
        else:
            print("✅ Resultado:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
    except Exception as e:
        logger.exception(f"Erro ao executar ferramenta: {e}")
        print(f"❌ Erro ao executar ferramenta: {e}")


# Funções de comando para o CLI
def main_configurar(session_id: Optional[str] = None) -> None:
    """Função de comando para configurar o MCP."""
    if not MCPRUN_SIMPLE_AVAILABLE:
        print("❌ Adaptador MCPRunClient não está disponível")
        return
    
    configurar_mcp(session_id)


def main_listar() -> None:
    """Função de comando para listar ferramentas MCP."""
    if not MCPRUN_SIMPLE_AVAILABLE:
        print("❌ Adaptador MCPRunClient não está disponível")
        return
    
    listar_ferramentas()


def main_executar(nome: str, params_json: Optional[str] = None) -> None:
    """Função de comando para executar uma ferramenta MCP."""
    if not MCPRUN_SIMPLE_AVAILABLE:
        print("❌ Adaptador MCPRunClient não está disponível")
        return
    
    executar_ferramenta(nome, params_json) 