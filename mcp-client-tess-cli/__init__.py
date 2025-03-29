"""
Camada de infraestrutura da aplicação.

Este pacote contém as implementações concretas das interfaces definidas
na camada de domínio, seguindo o princípio de inversão de dependência
da Arquitetura Limpa.

Componentes principais:
- providers: Implementações dos provedores de serviços externos
- repositories: Implementações dos repositórios de dados
- adapters: Adaptadores para sistemas externos
"""

from .providers import ProviderFactory, TessProvider, get_provider, create_provider

__all__ = [
    'ProviderFactory',
    'TessProvider',
    'get_provider',
    'create_provider',
]
