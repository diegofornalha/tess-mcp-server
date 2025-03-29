"""
Provedor para interação com o MCP (Model Context Protocol)

Este módulo contém uma implementação deprecada que será removida em versões futuras.
Utilize infrastructure.providers.mcp_provider em vez disso.
"""

import os
import json
import warnings
import logging
from typing import Dict, Optional, Any
from pathlib import Path

# Configuração de logging
from ..utils.logging import get_logger
logger = get_logger(__name__)

# Importar provedor da camada de infraestrutura
try:
    from infrastructure.providers import MCPProvider as InfraMCPProvider
except ImportError:
    # Fallback para implementação local se a importação falhar
    logger.warning("Não foi possível importar MCPProvider da infrastructure. Usando implementação local.")
    InfraMCPProvider = None


class MCPProvider:
    """
    Classe para gerenciar a configuração do MCP.run.
    
    DEPRECATED: Esta classe é um adaptador para a implementação em 
    infrastructure.providers.MCPProvider e está mantida para compatibilidade.
    """
    
    def __init__(self):
        """
        Inicializa o provedor MCP.
        
        Emite um aviso de depreciação recomendando o uso da implementação
        da camada de infraestrutura.
        """
        warnings.warn(
            "Esta implementação do MCPProvider está depreciada. "
            "Use infrastructure.providers.MCPProvider para novas implementações.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Tentar usar a implementação da infraestrutura se disponível
        if InfraMCPProvider:
            try:
                self._infra_provider = InfraMCPProvider()
                self._using_infra = True
                logger.info("Usando implementação da camada de infraestrutura para o MCPProvider")
            except Exception as e:
                logger.warning(f"Erro ao inicializar provedor MCP da infraestrutura: {str(e)}")
                self._using_infra = False
        else:
            self._using_infra = False
    
    def get_mcp_session_id(self) -> Optional[str]:
        """Obtém o ID de sessão MCP.run das configurações salvas."""
        if self._using_infra:
            return self._infra_provider.get_mcp_session_id()
        
        # Implementação legada - mantida para compatibilidade
        # Primeiro verifica se temos a variável de ambiente
        session_id = os.environ.get("MCP_SESSION_ID")
        if session_id:
            logger.info("Usando ID de sessão MCP da variável de ambiente")
            return session_id
            
        # Caso contrário, verifica o arquivo de configuração
        config_file = os.path.expanduser("~/.arcee/config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    if "mcp_session_id" in config:
                        logger.info("Usando ID de sessão MCP do arquivo de configuração")
                        return config["mcp_session_id"]
            except Exception as e:
                logger.error(f"Erro ao ler configuração do MCP: {str(e)}")
                
        return None
    
    def save_mcp_session_id(self, session_id: str) -> bool:
        """Salva o ID de sessão MCP.run nas configurações locais."""
        if self._using_infra:
            return self._infra_provider.save_mcp_session_id(session_id)
        
        # Implementação legada - mantida para compatibilidade
        try:
            # Garante que o diretório de configuração existe
            config_dir = os.path.expanduser("~/.arcee")
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            config_file = os.path.join(config_dir, "config.json")
            
            # Lê a configuração atual, se existir
            config = {}
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        config = json.load(f)
                except:
                    logger.warning("Arquivo de configuração existente não pôde ser lido. Criando novo.")
            
            # Atualiza a configuração
            config["mcp_session_id"] = session_id
            
            # Salva a configuração
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
                
            logger.info(f"ID de sessão MCP salvo com sucesso em {config_file}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configuração do MCP: {str(e)}")
            return False
    
    def check_mcp_configured(self) -> bool:
        """Verifica se o MCP está configurado."""
        if self._using_infra:
            return self._infra_provider.check_mcp_configured()
        
        # Implementação legada - mantida para compatibilidade
        return self.get_mcp_session_id() is not None
    
    def clear_mcp_config(self) -> bool:
        """Limpa a configuração do MCP."""
        if self._using_infra:
            return self._infra_provider.clear_mcp_config()
        
        # Implementação legada - mantida para compatibilidade
        config_file = os.path.expanduser("~/.arcee/config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                if "mcp_session_id" in config:
                    del config["mcp_session_id"]
                    
                    with open(config_file, "w", encoding="utf-8") as f:
                        json.dump(config, f, indent=2)
                        
                    logger.info("Configuração do MCP removida com sucesso")
                return True
            except Exception as e:
                logger.error(f"Erro ao limpar configuração do MCP: {str(e)}")
                
        return False 