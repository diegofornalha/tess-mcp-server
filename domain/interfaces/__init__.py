"""
Interfaces do domínio que definem contratos para implementações na camada de infraestrutura.

Seguindo o princípio de inversão de dependência da Arquitetura Limpa, estas
interfaces permitem que o domínio defina os contratos que serão implementados
pelas camadas externas, mantendo a independência do núcleo da aplicação.
"""

from .providers import (
    TessProviderInterface, 
    MCPProviderInterface, 
    ProviderFactoryInterface,
    ArceeProviderInterface
)
from .mcp_server import MCPServerInterface
from .mcp_client import MCPClientInterface

__all__ = [
    "TessProviderInterface",
    "MCPProviderInterface",
    "ProviderFactoryInterface",
    "ArceeProviderInterface",
    "MCPServerInterface",
    "MCPClientInterface",
] 