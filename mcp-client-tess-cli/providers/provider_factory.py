#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fábrica para criar provedores de serviços, seguindo o padrão Factory.
"""

import os
import logging
from typing import Optional, Any, Dict
from domain.interfaces import ProviderFactoryInterface

logger = logging.getLogger(__name__)

# Instâncias globais dos provedores para reutilização (padrão singleton)
_providers = {}


class ProviderFactory(ProviderFactoryInterface):
    """
    Implementação concreta da fábrica de provedores que segue a interface definida no domínio.
    """
    
    def get_provider(self, api_key: Optional[str] = None, api_url: Optional[str] = None) -> Any:
        """
        Retorna uma instância do provedor padrão (singleton).
        
        Args:
            api_key: Chave de API opcional
            api_url: URL da API opcional
            
        Returns:
            Any: Instância do provedor padrão (TessProvider)
        """
        # Por padrão, retornamos o provedor TESS
        return self.create_provider("tess", api_key, api_url)

    def create_provider(self, provider_type: str, api_key: Optional[str] = None, api_url: Optional[str] = None) -> Any:
        """
        Cria uma instância do provedor especificado ou retorna uma instância existente.
        
        Args:
            provider_type: Tipo de provedor a ser criado ("tess", "mcp", etc.)
            api_key: Chave de API opcional
            api_url: URL da API opcional
            
        Returns:
            Any: Instância do provedor solicitado
            
        Raises:
            ValueError: Se o tipo de provedor não for suportado
        """
        global _providers
        provider_type = provider_type.lower()
        
        # Verificar se já temos uma instância deste provedor
        if provider_type in _providers:
            return _providers[provider_type]
        
        # Importação tardia para evitar dependência circular
        from .tess_provider import TessProvider
        
        # Criar nova instância do provedor
        try:
            if provider_type == "tess":
                # Se não foi fornecida uma chave de API, tentamos usar a variável de ambiente
                if not api_key:
                    api_key = os.getenv("TESS_API_KEY")
                
                # Se não foi fornecida uma URL de API, tentamos usar a variável de ambiente
                if not api_url:
                    api_url = os.getenv("TESS_API_URL", "https://tess.pareto.io/api")
                
                provider = TessProvider(api_key, api_url)
                _providers[provider_type] = provider
                return provider
            else:
                raise ValueError(f"Provedor não suportado: {provider_type}")
        except Exception as e:
            logger.error(f"Erro ao criar provedor {provider_type}: {str(e)}")
            raise


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
