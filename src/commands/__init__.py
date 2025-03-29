#!/usr/bin/env python
"""
Comandos disponíveis para a CLI Arcee/TESS.

Este pacote contém os comandos disponíveis para a CLI.
"""

# Comandos MCP (legados)
from .mcp import main_configurar, main_listar, main_executar

# Comando de chat
from .chat import main as chat_main

# Novos comandos de ferramentas MCP
from .mcp_tools import (
    main_listar as mcp_tools_listar,
    main_buscar as mcp_tools_buscar,
    main_detalhes as mcp_tools_detalhes,
    main_executar as mcp_tools_executar
)

__all__ = [
    # Comandos MCP legados
    "main_configurar",
    "main_listar",
    "main_executar",
    
    # Comando de chat
    "chat_main",
    
    # Novos comandos de ferramentas MCP
    "mcp_tools_listar",
    "mcp_tools_buscar",
    "mcp_tools_detalhes",
    "mcp_tools_executar"
] 