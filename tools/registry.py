#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Registro Centralizado de Ferramentas

Este módulo implementa um registro centralizado para todas as ferramentas 
disponíveis no projeto crew_ai_tess_pareto, resolvendo a duplicação 
entre 'src/tools' e 'tools/'.

Princípios:
1. Registro único para todas as ferramentas
2. Nomenclatura padronizada
3. Compatibilidade com implementações existentes
4. Processo de migração gradual
"""

import os
import logging
import warnings
from typing import Dict, Any, List, Type, Optional, Callable, Union, TypeVar

# Configuração de logging
logger = logging.getLogger(__name__)

# Importação das ferramentas disponíveis
# Primeiro importamos das implementações canônicas
try:
    from .mcpx_simple import MCPRunClient
    from .tess_nl_processor import TessNLProcessor
    from .mcpx_tools import MCPTool, get_mcprun_tools
except ImportError as e:
    logger.warning(f"Não foi possível importar ferramenta: {e}")

# Definição de tipo para ferramentas
T = TypeVar('T')

class ToolRegistry:
    """
    Registro centralizado de ferramentas.
    
    Esta classe implementa o padrão Registry para gerenciar todas 
    as ferramentas disponíveis no projeto.
    """
    
    # Dicionário para armazenar ferramentas recomendadas (atuais)
    _recommended: Dict[str, Any] = {}
    
    # Dicionário para armazenar ferramentas legadas (a serem depreciadas)
    _legacy: Dict[str, Any] = {}
    
    # Metadados associados a cada ferramenta
    _metadata: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def register(cls, name: str, tool: Any, deprecated: bool = False, **metadata) -> None:
        """
        Registra uma ferramenta no registro centralizado.
        
        Args:
            name: Nome único da ferramenta
            tool: Classe ou função da ferramenta
            deprecated: Indica se a ferramenta está depreciada
            **metadata: Metadados adicionais (descrição, versão, etc.)
        """
        # Determinar em qual registro adicionar
        target_registry = cls._legacy if deprecated else cls._recommended
        
        # Adicionar metadados
        metadata["deprecated"] = deprecated
        if "description" not in metadata:
            # Tentar extrair descrição da docstring
            metadata["description"] = tool.__doc__ or "Sem descrição disponível"
            
        # Registrar ferramenta
        target_registry[name] = tool
        cls._metadata[name] = metadata
        
        log_msg = f"Ferramenta registrada: {name}"
        if deprecated:
            log_msg += " (depreciada)"
        logger.debug(log_msg)
    
    @classmethod
    def get(cls, name: str, allow_deprecated: bool = True) -> Any:
        """
        Obtém uma ferramenta pelo nome.
        
        Args:
            name: Nome da ferramenta
            allow_deprecated: Se True, verifica também ferramentas depreciadas
            
        Returns:
            A ferramenta solicitada
            
        Raises:
            KeyError: Se a ferramenta não for encontrada
        """
        # Verificar primeiro nas ferramentas recomendadas
        if name in cls._recommended:
            return cls._recommended[name]
            
        # Se permitido, verificar nas ferramentas depreciadas
        if allow_deprecated and name in cls._legacy:
            metadata = cls._metadata.get(name, {})
            warning_message = metadata.get(
                "deprecation_message", 
                f"A ferramenta '{name}' está depreciada e será removida em versões futuras"
            )
            warnings.warn(warning_message, DeprecationWarning, stacklevel=2)
            return cls._legacy[name]
            
        # Se não encontrou
        raise KeyError(f"Ferramenta não encontrada: {name}")
    
    @classmethod
    def list(cls, include_deprecated: bool = False) -> Dict[str, Dict[str, Any]]:
        """
        Lista todas as ferramentas disponíveis com seus metadados.
        
        Args:
            include_deprecated: Se True, inclui ferramentas depreciadas
            
        Returns:
            Dicionário com ferramentas e seus metadados
        """
        result = {}
        
        # Adicionar ferramentas recomendadas
        for name in cls._recommended:
            result[name] = cls._metadata.get(name, {"deprecated": False})
            
        # Adicionar ferramentas depreciadas se solicitado
        if include_deprecated:
            for name in cls._legacy:
                result[name] = cls._metadata.get(name, {"deprecated": True})
                
        return result
    
    @classmethod
    def factory(cls, name: str, *args, **kwargs) -> Any:
        """
        Cria uma instância de uma ferramenta.
        
        Args:
            name: Nome da ferramenta
            *args: Argumentos posicionais para o construtor
            **kwargs: Argumentos nomeados para o construtor
            
        Returns:
            Uma instância da ferramenta solicitada
            
        Raises:
            KeyError: Se a ferramenta não for encontrada
        """
        tool_class = cls.get(name)
        return tool_class(*args, **kwargs)


# Registro das ferramentas recomendadas
ToolRegistry.register(
    "mcp_client", 
    MCPRunClient,
    description="Cliente para interação com o protocolo MCP.run",
    version="1.0.0"
)

ToolRegistry.register(
    "nl_processor", 
    TessNLProcessor,
    description="Processador de linguagem natural para comandos do TESS",
    version="1.0.0"
)

ToolRegistry.register(
    "get_mcprun_tools", 
    get_mcprun_tools,
    description="Obtém ferramentas MCP.run para uso com CrewAI",
    version="1.0.0"
)

# Registrar versões depreciadas (importando de src/tools)
try:
    from src.tools.mcpx_simple import MCPRunClient as MCPRunClientLegacy
    ToolRegistry.register(
        "mcp_client_legacy", 
        MCPRunClientLegacy,
        deprecated=True,
        deprecation_message="Use tools.registry.get('mcp_client') em vez de src.tools.mcpx_simple.MCPRunClient",
        version="0.9.0"
    )
except ImportError:
    logger.debug("Implementação legada de MCPRunClient não encontrada em src/tools")

try:
    from src.tools.mcp_nl_processor import MCPNLProcessor
    ToolRegistry.register(
        "mcp_nl_processor", 
        MCPNLProcessor,
        deprecated=True,
        deprecation_message="Use tools.registry.get('nl_processor') em vez de src.tools.mcp_nl_processor.MCPNLProcessor",
        version="0.9.0"
    )
except ImportError:
    logger.debug("Implementação de MCPNLProcessor não encontrada em src/tools")


# Atalhos para funções comuns
def get_mcp_client(*args, **kwargs) -> MCPRunClient:
    """
    Obtém uma instância do cliente MCP.run.
    
    Args:
        *args: Argumentos posicionais para o construtor
        **kwargs: Argumentos nomeados para o construtor
        
    Returns:
        Uma instância de MCPRunClient
    """
    return ToolRegistry.factory("mcp_client", *args, **kwargs)

def get_nl_processor(*args, **kwargs) -> TessNLProcessor:
    """
    Obtém uma instância do processador de linguagem natural do TESS.
    
    Args:
        *args: Argumentos posicionais para o construtor
        **kwargs: Argumentos nomeados para o construtor
        
    Returns:
        Uma instância de TessNLProcessor
    """
    return ToolRegistry.factory("nl_processor", *args, **kwargs)


# Exportar símbolos públicos
__all__ = [
    # Classes principais
    "ToolRegistry",
    
    # Implementações recomendadas
    "MCPRunClient",
    "TessNLProcessor",
    "get_mcprun_tools",
    
    # Funções auxiliares
    "get_mcp_client",
    "get_nl_processor",
] 