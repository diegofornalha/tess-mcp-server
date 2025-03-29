"""
Módulo de provedores de serviço.

DEPRECATED: Este módulo está sendo mantido por compatibilidade.
Use o módulo infrastructure.providers para novas implementações.
"""

import warnings

# Emitir aviso de depreciação ao importar este módulo
warnings.warn(
    "O módulo src.providers está depreciado. "
    "Use infrastructure.providers para novas implementações.",
    DeprecationWarning,
    stacklevel=2
)

# Importar classes adaptadoras
from .tess_provider import TessProvider
from .mcp_provider import MCPProvider
from .arcee_provider import ArceeProvider
from .provider_factory import ProviderFactory

# Exportar todas as classes adaptadoras
__all__ = [
    'TessProvider',
    'MCPProvider',
    'ArceeProvider',
    'ProviderFactory'
] 