"""
Fábrica para criação de provedores de serviço.

DEPRECATED: Este módulo está sendo mantido por compatibilidade.
Use infrastructure.providers.ProviderFactory para novas implementações.
"""

import warnings
import logging
from typing import Dict, Optional, Any, Type, Union

# Configuração de logging
from ..utils.logging import get_logger
logger = get_logger(__name__)

# Importações locais para compatibilidade
from .tess_provider import TessProvider
from .mcp_provider import MCPProvider
from .arcee_provider import ArceeProvider

# Importar fábrica da camada de infraestrutura
try:
    from infrastructure.providers import ProviderFactory as InfraProviderFactory
except ImportError:
    # Fallback para implementação local se a importação falhar
    logger.warning("Não foi possível importar ProviderFactory da infrastructure. Usando implementação local.")
    InfraProviderFactory = None


class ProviderFactory:
    """
    Fábrica para criação de provedores de serviço.
    
    DEPRECATED: Esta classe é um adaptador para a implementação em 
    infrastructure.providers.ProviderFactory e está mantida para compatibilidade.
    """
    
    # Cache de instâncias de provedores para reutilização
    _provider_instances = {}
    
    @classmethod
    def get_provider(cls):
        """
        Retorna uma instância do provedor padrão (TessProvider).
        
        Returns:
            TessProvider: Instância do provedor TESS
        """
        warnings.warn(
            "ProviderFactory.get_provider() está depreciado. "
            "Use infrastructure.providers.ProviderFactory().get_provider() para novas implementações.",
            DeprecationWarning,
            stacklevel=2
        )
        
        return cls.create_provider("tess")
    
    @classmethod
    def create_provider(cls, provider_type: str, **kwargs) -> Any:
        """
        Cria uma instância do provedor especificado ou retorna uma instância existente.
        
        Args:
            provider_type (str): Tipo de provedor ("tess", "mcp", "arcee")
            **kwargs: Argumentos adicionais para o provedor
            
        Returns:
            Any: Instância do provedor solicitado
            
        Raises:
            ValueError: Se o tipo de provedor não for suportado
        """
        warnings.warn(
            f"ProviderFactory.create_provider('{provider_type}') está depreciado. "
            f"Use infrastructure.providers.ProviderFactory().create_provider('{provider_type}') para novas implementações.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Tentar usar a fábrica da infraestrutura se disponível
        if InfraProviderFactory:
            try:
                factory = InfraProviderFactory()
                return factory.create_provider(provider_type, **kwargs)
            except Exception as e:
                logger.warning(f"Erro ao criar provedor usando infraestrutura: {str(e)}")
                # Fallback para implementação local
        
        # Cache key para armazenar instâncias
        cache_key = f"{provider_type}_{str(kwargs)}"
        
        # Verificar se já existe uma instância no cache
        if cache_key in cls._provider_instances:
            logger.debug(f"Usando instância em cache para {provider_type}")
            return cls._provider_instances[cache_key]
        
        # Criar nova instância
        provider = None
        
        try:
            if provider_type.lower() == "tess":
                provider = TessProvider(**kwargs)
            elif provider_type.lower() == "mcp":
                provider = MCPProvider(**kwargs)
            elif provider_type.lower() == "arcee":
                provider = ArceeProvider(**kwargs)
            else:
                msg = f"Tipo de provedor não suportado: {provider_type}"
                logger.error(msg)
                raise ValueError(msg)
                
            # Guardar no cache
            cls._provider_instances[cache_key] = provider
            return provider
            
        except Exception as e:
            logger.error(f"Erro ao criar provedor {provider_type}: {str(e)}")
            raise 