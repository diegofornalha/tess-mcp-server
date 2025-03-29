#!/usr/bin/env python
"""
Cliente simplificado para o MCP.run.

DEPRECATED: Este módulo está obsoleto e será removido em versões futuras.
Use infrastructure.mcp_client.MCPClient em seu lugar.
"""

import os
import json
import logging
import warnings
from typing import Dict, List, Any, Optional

# Importar o adaptador
from ..adapters.mcp_client_adapter import MCPRunClient, configure_mcprun

logger = logging.getLogger(__name__)

# Emitir aviso de deprecação
warnings.warn(
    "O módulo mcpx_simple está obsoleto e será removido em versões futuras. "
    "Use infrastructure.mcp_client.MCPClient em seu lugar.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ["MCPRunClient", "configure_mcprun"] 