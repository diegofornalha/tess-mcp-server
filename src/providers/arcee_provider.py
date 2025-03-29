"""
Provedor para interação com a API da Arcee AI.

DEPRECATED: Este módulo está sendo mantido por compatibilidade.
Use infrastructure.providers.ArceeProvider para novas implementações.
"""

import os
import json
import time
import warnings
import logging
from typing import List, Dict, Optional, Any, Union
from pathlib import Path

# Configuração de logging
from ..utils.logging import get_logger
logger = get_logger(__name__)

# Importar provedor da camada de infraestrutura
try:
    from infrastructure.providers import ArceeProvider as InfraArceeProvider
except ImportError:
    # Fallback para implementação local se a importação falhar
    logger.warning("Não foi possível importar ArceeProvider da infrastructure. Usando implementação local.")
    InfraArceeProvider = None


class ArceeProvider:
    """
    Classe para interação com a API da Arcee AI.
    
    DEPRECATED: Esta classe é um adaptador para a implementação em 
    infrastructure.providers.ArceeProvider e está mantida para compatibilidade.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Inicializa o provedor Arcee.
        
        Args:
            api_key (str, optional): Chave de API da Arcee. Se não fornecida,
                tentará carregar da configuração ou variável de ambiente.
            model (str, optional): Modelo padrão a ser usado. 
        
        Emite um aviso de depreciação recomendando o uso da implementação
        da camada de infraestrutura.
        """
        warnings.warn(
            "Esta implementação do ArceeProvider está depreciada. "
            "Use infrastructure.providers.ArceeProvider para novas implementações.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Tentar usar a implementação da infraestrutura se disponível
        if InfraArceeProvider:
            try:
                self._infra_provider = InfraArceeProvider(api_key=api_key, model=model)
                self._using_infra = True
                logger.info("Usando implementação da camada de infraestrutura para o ArceeProvider")
            except Exception as e:
                logger.warning(f"Erro ao inicializar provedor Arcee da infraestrutura: {str(e)}")
                self._using_infra = False
        else:
            self._using_infra = False
            
        # Se não foi possível usar a infraestrutura, inicializa atributos locais
        if not self._using_infra:
            self.api_key = api_key or self._load_api_key_from_config()
            self.model = model or "default"
    
    def _load_api_key_from_config(self) -> Optional[str]:
        """Carrega a chave de API do arquivo de configuração ou variável de ambiente."""
        # Primeiro verifica se existe na variável de ambiente
        api_key = os.environ.get("ARCEE_API_KEY")
        if api_key:
            logger.info("Usando chave de API da Arcee da variável de ambiente")
            return api_key
            
        # Caso contrário, tenta carregar do arquivo de configuração
        config_file = os.path.expanduser("~/.arcee/config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if "arcee_api_key" in config:
                        logger.info("Usando chave de API da Arcee do arquivo de configuração")
                        return config["arcee_api_key"]
            except Exception as e:
                logger.error(f"Erro ao carregar configuração da Arcee: {str(e)}")
                
        return None
    
    def _save_api_key_to_config(self, api_key: str) -> bool:
        """Salva a chave de API no arquivo de configuração."""
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
            config["arcee_api_key"] = api_key
            
            # Salva a configuração
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
                
            logger.info("Chave de API da Arcee salva com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar chave de API da Arcee: {str(e)}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Verifica a saúde da API da Arcee.
        
        Returns:
            Dict[str, Any]: Resultado da verificação de saúde
        """
        if self._using_infra:
            return self._infra_provider.health_check()
            
        # Implementação legada
        logger.warning("Implementação legada de health_check não está completa")
        result = {
            "status": "error",
            "message": "Não foi possível se conectar à API da Arcee",
            "detail": "Implementação legada não suportada"
        }
        
        # Verifica se a chave de API está configurada
        if not self.api_key:
            result["detail"] = "Chave de API não configurada"
            return result
            
        return result
    
    def generate_content_chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None, 
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Gera conteúdo usando o recurso de chat.
        
        Args:
            messages (List[Dict[str, str]]): Lista de mensagens no formato 
                [{"role": "user", "content": "mensagem"}]
            model (str, optional): Modelo a ser usado. Se None, usa o modelo padrão.
            system_prompt (str, optional): Prompt de sistema. Se None, usa o padrão.
            context (Dict[str, Any], optional): Contexto adicional para o prompt.
            **kwargs: Argumentos adicionais para a API
            
        Returns:
            Dict[str, Any]: Resposta da API
        """
        if self._using_infra:
            return self._infra_provider.generate_content_chat(
                messages=messages, 
                model=model, 
                system_prompt=system_prompt,
                context=context,
                **kwargs
            )
            
        # Implementação legada
        logger.warning("Implementação legada de generate_content_chat não está completa")
        return {
            "status": "error",
            "message": "Funcionalidade não implementada na versão legada",
            "content": "Desculpe, esta funcionalidade não está disponível. Use a nova implementação em infrastructure.providers.ArceeProvider"
        }
        
    def chat(
        self, 
        message: str, 
        history: Optional[List[Dict[str, str]]] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Facilita uma interação de chat simples, mantendo o histórico de mensagens.
        
        Args:
            message (str): Mensagem do usuário
            history (List[Dict[str, str]], optional): Histórico de mensagens anteriores
            model (str, optional): Modelo a ser usado
            system_prompt (str, optional): Prompt de sistema
            **kwargs: Argumentos adicionais
            
        Returns:
            Dict[str, Any]: Resposta incluindo o texto gerado e histórico atualizado
        """
        if self._using_infra:
            return self._infra_provider.chat(
                message=message,
                history=history,
                model=model,
                system_prompt=system_prompt,
                **kwargs
            )
            
        # Implementação legada
        logger.warning("Implementação legada de chat não está completa")
        return {
            "status": "error",
            "message": "Funcionalidade não implementada na versão legada",
            "content": "Desculpe, esta funcionalidade não está disponível. Use a nova implementação em infrastructure.providers.ArceeProvider",
            "history": history or []
        }
    
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de modelos disponíveis.
        
        Returns:
            List[Dict[str, Any]]: Lista de modelos disponíveis
        """
        if self._using_infra:
            return self._infra_provider.get_models()
            
        # Implementação legada
        logger.warning("Implementação legada de get_models não está completa")
        return [
            {"id": "default", "name": "Modelo padrão (legado)", "description": "Este é apenas um placeholder para compatibilidade"}
        ]
    
    def set_model(self, model: str) -> bool:
        """
        Define o modelo padrão a ser usado.
        
        Args:
            model (str): ID do modelo
            
        Returns:
            bool: True se bem-sucedido, False caso contrário
        """
        if self._using_infra:
            return self._infra_provider.set_model(model)
            
        # Implementação legada
        logger.warning(f"Definindo modelo para {model} (legado)")
        self.model = model
        return True 