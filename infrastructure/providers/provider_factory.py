#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implementação da fábrica de provedores.
"""

import logging
from typing import Dict, Any, Optional, Type, Union
from domain.interfaces import ProviderFactoryInterface

from .tess_provider import TessProvider
from .mcp_provider import MCPProvider
from .arcee_provider import ArceeProvider

# Configuração do logger
logger = logging.getLogger(__name__)


class ProviderFactory(ProviderFactoryInterface):
    """
    Implementação concreta da fábrica de provedores de serviços
    que segue a interface definida no domínio.
    """
    
    # Cache de instâncias de provedores para reutilização
    _provider_instances = {}
    
    def get_provider(self, api_key: Optional[str] = None, 
                   api_url: Optional[str] = None) -> Any:
        """
        Retorna uma instância do provedor padrão (TessProvider).
        
        Args:
            api_key: Chave de API opcional
            api_url: URL da API opcional
            
        Returns:
            TessProvider: Instância do provedor TESS
        """
        # Por padrão, cria um TessProvider
        return self.create_provider("tess", api_key=api_key, api_url=api_url)
    
    def create_provider(self, provider_type: str, api_key: Optional[str] = None, 
                      api_url: Optional[str] = None, **kwargs) -> Any:
        """
        Cria uma instância do provedor especificado ou retorna uma instância existente.
        
        Args:
            provider_type: Tipo de provedor ("tess", "mcp", "arcee")
            api_key: Chave de API opcional
            api_url: URL da API opcional
            **kwargs: Argumentos adicionais para o provedor
            
        Returns:
            Any: Instância do provedor solicitado
            
        Raises:
            ValueError: Se o tipo de provedor não for suportado
        """
        # Cache key para armazenar instâncias
        cache_key = f"{provider_type}_{api_key}_{api_url}_{str(kwargs)}"
        
        # Verificar se já existe uma instância no cache
        if cache_key in self._provider_instances:
            logger.debug(f"Usando instância em cache para {provider_type}")
            return self._provider_instances[cache_key]
        
        # Criar nova instância
        provider = None
        
        try:
            if provider_type.lower() == "tess":
                provider = TessProvider(api_key=api_key, api_url=api_url, **kwargs)
            elif provider_type.lower() == "mcp":
                provider = MCPProvider(**kwargs)
            elif provider_type.lower() == "arcee":
                provider = ArceeProvider(api_key=api_key, **kwargs)
            else:
                msg = f"Tipo de provedor não suportado: {provider_type}"
                logger.error(msg)
                raise ValueError(msg)
                
            # Guardar no cache
            self._provider_instances[cache_key] = provider
            return provider
            
        except Exception as e:
            logger.error(f"Erro ao criar provedor {provider_type}: {str(e)}")
            raise
    
    def get_provider_by_config(self, config: Dict[str, Any]) -> Any:
        """
        Cria um provedor com base em um dicionário de configuração.
        
        Args:
            config: Dicionário com a configuração do provedor
            
        Returns:
            Any: Instância do provedor
            
        Raises:
            ValueError: Se a configuração for inválida
        """
        if "type" not in config:
            raise ValueError("Configuração não contém o tipo de provedor")
            
        provider_type = config.pop("type")
        return self.create_provider(provider_type, **config)
    
    def list_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """
        Lista todos os provedores disponíveis com seus metadados.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dicionário de provedores disponíveis
        """
        return {
            "tess": {
                "name": "TESS Provider",
                "description": "Provedor para acesso ao serviço TESS",
                "class": TessProvider
            },
            "mcp": {
                "name": "MCP Provider",
                "description": "Provedor para acesso ao MCP.run",
                "class": MCPProvider
            },
            "arcee": {
                "name": "Arcee Provider",
                "description": "Provedor para acesso à API da Arcee AI",
                "class": ArceeProvider
            }
        }
    
    def clear_provider_cache(self) -> None:
        """
        Limpa o cache de provedores.
        """
        self._provider_instances.clear()
        logger.info("Cache de provedores limpo")


# Para compatibilidade com código existente, exportamos funções de conveniência
def get_provider(api_key: Optional[str] = None, api_url: Optional[str] = None) -> Any:
    """
    Função de compatibilidade para obter um provedor através da fábrica.
    """
    factory = ProviderFactory()
    return factory.get_provider(api_key, api_url)


def create_provider(provider_type: str, api_key: Optional[str] = None, api_url: Optional[str] = None) -> Any:
    """
    Função de compatibilidade para criar um provedor através da fábrica.
    """
    factory = ProviderFactory()
    return factory.create_provider(provider_type, api_key, api_url) 