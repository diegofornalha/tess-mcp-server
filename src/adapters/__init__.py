#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adaptadores para compatibilidade com código legado.

Este módulo contém adaptadores que facilitam a transição gradual
para a nova arquitetura, mantendo compatibilidade com código legado.
"""

from .mcp_client_adapter import MCPRunClient, configure_mcprun

__all__ = ["MCPRunClient", "configure_mcprun"] 