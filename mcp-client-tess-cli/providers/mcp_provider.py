#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implementação do provedor para acesso ao MCP.run
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from domain.interfaces import MCPProviderInterface

# Configuração do logger
logger = logging.getLogger(__name__)

# Constantes para a configuração do MCP
CONFIG_DIR = Path.home() / ".tess"
MCP_CONFIG_FILE = CONFIG_DIR / "mcp_config.json"

class MCPProvider(MCPProviderInterface):
    """
    Implementação concreta do provedor para acesso ao MCP.run
    que segue a interface definida no domínio.
    """
    
    def get_mcp_session_id(self) -> Optional[str]:
        """
        Obtém o ID de sessão MCP.run das configurações salvas.
        
        Returns:
            Optional[str]: ID de sessão do MCP.run ou None se não configurado
        """
        # Primeiro verifica se temos a variável de ambiente
        session_id = os.environ.get("MCP_SESSION_ID")
        if session_id:
            logger.info("Usando ID de sessão MCP da variável de ambiente")
            return session_id
            
        # Caso contrário, verifica o arquivo de configuração
        if MCP_CONFIG_FILE.exists():
            try:
                with open(MCP_CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    if "session_id" in config:
                        logger.info("Usando ID de sessão MCP do arquivo de configuração")
                        return config["session_id"]
            except Exception as e:
                logger.error(f"Erro ao ler configuração do MCP: {str(e)}")
                
        return None
        
    def save_mcp_session_id(self, session_id: str) -> bool:
        """
        Salva o ID de sessão MCP.run nas configurações locais.
        
        Args:
            session_id: ID de sessão do MCP.run
            
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        try:
            # Garante que o diretório de configuração existe
            CONFIG_DIR.mkdir(exist_ok=True, parents=True)
            
            # Lê a configuração atual, se existir
            config = {}
            if MCP_CONFIG_FILE.exists():
                try:
                    with open(MCP_CONFIG_FILE, "r", encoding="utf-8") as f:
                        config = json.load(f)
                except:
                    logger.warning("Arquivo de configuração existente não pôde ser lido. Criando novo.")
            
            # Atualiza a configuração
            config["session_id"] = session_id
            
            # Salva a configuração
            with open(MCP_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
                
            logger.info(f"ID de sessão MCP salvo com sucesso em {MCP_CONFIG_FILE}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configuração do MCP: {str(e)}")
            return False
            
    def check_mcp_configured(self) -> bool:
        """
        Verifica se o MCP está configurado.
        
        Returns:
            bool: True se configurado, False caso contrário
        """
        return self.get_mcp_session_id() is not None
        
    def clear_mcp_config(self) -> bool:
        """
        Limpa a configuração do MCP.
        
        Returns:
            bool: True se limpou com sucesso, False caso contrário
        """
        try:
            if MCP_CONFIG_FILE.exists():
                MCP_CONFIG_FILE.unlink()
                logger.info("Configuração do MCP removida com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar configuração do MCP: {str(e)}")
            return False 