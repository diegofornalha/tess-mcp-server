"""
Provedores de serviços implementados na camada de infraestrutura.

Este pacote contém implementações concretas dos provedores definidos
como interfaces na camada de domínio, seguindo o princípio de inversão
de dependência da Arquitetura Limpa.
"""

from .provider_factory import ProviderFactory, get_provider, create_provider
from .tess_provider import TessProvider

__all__ = [
    'ProviderFactory',
    'TessProvider',
    'get_provider',
    'create_provider',
]
