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
        
        # Verificar também na pasta .arcee para compatibilidade com versões anteriores
        legacy_config = Path.home() / ".arcee" / "config.json"
        if legacy_config.exists():
            try:
                with open(legacy_config, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    if "mcp_session_id" in config:
                        logger.info("Usando ID de sessão MCP do arquivo de configuração legado")
                        # Migra a configuração para o novo local
                        self.save_mcp_session_id(config["mcp_session_id"])
                        return config["mcp_session_id"]
            except Exception as e:
                logger.error(f"Erro ao ler configuração legada do MCP: {str(e)}")
                
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
            
            # Para compatibilidade, também salvamos no local antigo
            try:
                legacy_dir = Path.home() / ".arcee"
                legacy_dir.mkdir(exist_ok=True, parents=True)
                legacy_config = legacy_dir / "config.json"
                
                old_config = {}
                if legacy_config.exists():
                    with open(legacy_config, "r", encoding="utf-8") as f:
                        old_config = json.load(f)
                
                old_config["mcp_session_id"] = session_id
                
                with open(legacy_config, "w", encoding="utf-8") as f:
                    json.dump(old_config, f, indent=2)
                    
                logger.debug("ID de sessão MCP também salvo no formato legado para compatibilidade")
            except Exception as e:
                logger.warning(f"Não foi possível salvar configuração legada: {str(e)}")
            
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
            success = True
            
            # Remove configuração nova
            if MCP_CONFIG_FILE.exists():
                MCP_CONFIG_FILE.unlink()
                logger.info("Configuração do MCP removida com sucesso")
            
            # Remove também da configuração legada
            legacy_config = Path.home() / ".arcee" / "config.json"
            if legacy_config.exists():
                try:
                    with open(legacy_config, "r", encoding="utf-8") as f:
                        config = json.load(f)
                    
                    if "mcp_session_id" in config:
                        del config["mcp_session_id"]
                        
                        with open(legacy_config, "w", encoding="utf-8") as f:
                            json.dump(config, f, indent=2)
                            
                        logger.info("Configuração legada do MCP também foi removida")
                except Exception as e:
                    logger.warning(f"Erro ao limpar configuração legada: {str(e)}")
                    success = False
            
            return success
        except Exception as e:
            logger.error(f"Erro ao limpar configuração do MCP: {str(e)}")
            return False
            
    def get_mcp_config(self) -> Dict[str, Any]:
        """
        Obtém a configuração completa do MCP.
        
        Returns:
            Dict[str, Any]: Configuração do MCP ou dicionário vazio se não configurado
        """
        config = {}
        
        if MCP_CONFIG_FILE.exists():
            try:
                with open(MCP_CONFIG_FILE, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception as e:
                logger.error(f"Erro ao ler configuração do MCP: {str(e)}")
        
        return config
    
    def save_mcp_config(self, config: Dict[str, Any]) -> bool:
        """
        Salva a configuração completa do MCP.
        
        Args:
            config: Configuração a ser salva
            
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        try:
            # Garante que o diretório de configuração existe
            CONFIG_DIR.mkdir(exist_ok=True, parents=True)
            
            # Salva a configuração
            with open(MCP_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
                
            logger.info(f"Configuração do MCP salva com sucesso em {MCP_CONFIG_FILE}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configuração do MCP: {str(e)}")
            return False 