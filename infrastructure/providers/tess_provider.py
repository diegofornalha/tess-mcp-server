#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implementação do provider para o serviço TESS (Tess AI API).

O TESS é uma plataforma que oferece APIs para integração de agentes de IA
e capacidades de gerenciamento de arquivos em aplicações. Este módulo implementa
o cliente para comunicação com a API TESS, permitindo listar, executar agentes
e gerenciar arquivos.
"""

import os
import time
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Tuple

from domain.interfaces.providers import TessProviderInterface

logger = logging.getLogger(__name__)


class TessProvider(TessProviderInterface):
    """
    Provider para acesso ao serviço TESS (Tess AI API).
    
    Esta classe implementa a interface TessProviderInterface para comunicação
    com a API TESS (https://tess.pareto.io/api), permitindo o uso de
    agentes de IA e gerenciamento de arquivos.
    """
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        Inicializa o provider TESS.
        
        Args:
            api_key: Chave de API do TESS (opcional, pode ser carregada do ambiente)
            api_url: URL base da API TESS (opcional, usa o valor padrão se não fornecido)
        
        Raises:
            ValueError: Se não for possível obter uma API key válida
        """
        # Tentar obter a chave API de várias fontes
        self.api_key = api_key or os.getenv("TESS_API_KEY") or self._load_api_key_from_config()
        
        # Definir URL da API (use local se configurado)
        self.use_local = os.getenv("USE_LOCAL_TESS", "False").lower() in ["true", "1", "t"]
        
        if self.use_local:
            self.api_url = os.getenv("TESS_LOCAL_SERVER_URL", "http://localhost:3001")
        else:
            self.api_url = api_url or os.getenv("TESS_API_URL", "https://tess.pareto.io")
            
        # Adicionar /api ao final se não estiver presente
        if not self.api_url.endswith("/api"):
            self.api_url = f"{self.api_url}/api"
            
        logger.debug(f"Inicializado provider TESS com URL: {self.api_url}")
        
        # Verificar se temos uma chave API (não necessária para uso local)
        if not self.api_key and not self.use_local:
            raise ValueError("Chave API não fornecida e USE_LOCAL_TESS não está ativado")
    
    def _load_api_key_from_config(self) -> Optional[str]:
        """
        Carrega a chave API do arquivo de configuração.
        
        Returns:
            str: Chave API ou None se não encontrada
        """
        try:
            # Verificar configuração nova
            config_path = os.path.expanduser("~/.arcee/config.json")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    if "tess_api_key" in config:
                        return config["tess_api_key"]
            
            # Verificar configuração legada
            legacy_path = os.path.expanduser("~/.tess/config.json")
            if os.path.exists(legacy_path):
                with open(legacy_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    if "api_key" in config:
                        return config["api_key"]
        except Exception as e:
            logger.error(f"Erro ao carregar chave API do TESS: {e}")
        
        return None
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Faz uma requisição para a API TESS.
        
        Args:
            method: Método HTTP (GET, POST, etc)
            endpoint: Endpoint da API (sem a base URL)
            **kwargs: Argumentos adicionais para requests
            
        Returns:
            Dict[str, Any]: Resposta da API
            
        Raises:
            RuntimeError: Se houver erro na requisição
        """
        # Adicionar headers de autenticação se não estiver em modo local
        headers = kwargs.pop("headers", {})
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Adicionar content-type se não específicado
        if "files" not in kwargs and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"
        
        # Construir URL completa
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        
        # Log da requisição para debug
        logger.debug(f"Requisição TESS: {method} {url}")
        if "json" in kwargs:
            logger.debug(f"Payload: {kwargs['json']}")
        
        try:
            # Fazer requisição
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            
            # Log da resposta para debug
            logger.debug(f"Resposta TESS: {response.status_code}")
            logger.debug(f"Headers: {response.headers}")
            
            # Verificar se a resposta é JSON
            if "application/json" in response.headers.get("Content-Type", ""):
                try:
                    data = response.json()
                    logger.debug(f"Resposta JSON: {json.dumps(data)[:500]}...")
                except Exception:
                    logger.warning("Falha ao decodificar resposta JSON")
                    data = {}
            else:
                data = {"text": response.text}
            
            # Validar resposta
            response.raise_for_status()
            
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição TESS: {str(e)}")
            raise RuntimeError(f"Erro ao comunicar com API TESS: {str(e)}")
    
    def health_check(self) -> Tuple[bool, str]:
        """
        Verifica a conexão com a API TESS.
        
        Returns:
            Tuple[bool, str]: Status da conexão (True/False) e mensagem explicativa
        """
        try:
            # Verificar fazendo uma requisição simples para a API
            start_time = time.time()
            self._make_request("GET", "agents", params={"per_page": 1})
            elapsed = time.time() - start_time
            
            return True, f"Conexão com TESS estabelecida em {elapsed:.2f}s"
        except Exception as e:
            logger.error(f"Falha na verificação de saúde do TESS: {e}")
            return False, f"Erro de conexão com TESS: {str(e)}"
    
    def list_agents(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Lista os agentes disponíveis no TESS.
        
        Args:
            filters: Filtros opcionais para a busca (ex: page, per_page, q, type)
            
        Returns:
            List[Dict[str, Any]]: Lista de agentes disponíveis
        """
        try:
            # Configurar parâmetros de paginação e filtros
            params = filters or {}
            
            # Fazer requisição para obter agentes
            response = self._make_request("GET", "agents", params=params)
            
            # Extrair lista de agentes da resposta
            if "data" in response:
                agents = response["data"]
                logger.info(f"Obtidos {len(agents)} agentes do TESS")
                return agents
            else:
                logger.warning("Resposta da API TESS não contém campo 'data'")
                return []
                
        except Exception as e:
            logger.error(f"Erro ao listar agentes TESS: {e}")
            raise RuntimeError(f"Falha ao listar agentes: {str(e)}")
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes de um agente específico.
        
        Args:
            agent_id: ID do agente
            
        Returns:
            Dict[str, Any]: Detalhes do agente
            
        Raises:
            ValueError: Se o agente não for encontrado
        """
        try:
            # Fazer requisição para obter detalhes do agente
            response = self._make_request("GET", f"agents/{agent_id}")
            
            # Verificar se a resposta contém os dados do agente
            if "data" in response:
                agent = response["data"]
                logger.info(f"Obtidos detalhes do agente {agent_id}")
                return agent
            else:
                logger.warning(f"Resposta da API TESS para agente {agent_id} não contém campo 'data'")
                raise ValueError(f"Agente não encontrado: {agent_id}")
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.error(f"Agente não encontrado: {agent_id}")
                raise ValueError(f"Agente não encontrado: {agent_id}")
            else:
                logger.error(f"Erro HTTP ao obter agente {agent_id}: {e}")
                raise RuntimeError(f"Falha ao obter agente: {str(e)}")
        except Exception as e:
            logger.error(f"Erro ao obter agente {agent_id}: {e}")
            raise RuntimeError(f"Falha ao obter agente: {str(e)}")
    
    def execute_agent(self, agent_id: str, input_text: str, **kwargs) -> Dict[str, Any]:
        """
        Executa um agente específico com o texto fornecido.
        
        Args:
            agent_id: ID do agente a ser executado
            input_text: Texto de entrada para o agente
            **kwargs: Parâmetros adicionais para a execução (ex: temperature, model)
            
        Returns:
            Dict[str, Any]: Resultado da execução
            
        Raises:
            ValueError: Se o agente não for encontrado
            RuntimeError: Se houver erro na execução
        """
        try:
            # Construir mensagem do usuário
            messages = [{"role": "user", "content": input_text}]
            
            # Mesclar kwargs com defaults
            params = {
                "temperature": kwargs.get("temperature", "1"),
                "model": kwargs.get("model", "tess-ai-light"),
                "messages": messages,
                "tools": kwargs.get("tools", "no-tools"),
                "waitExecution": kwargs.get("wait_execution", False),
            }
            
            # Adicionar file_ids se fornecidos
            if "file_ids" in kwargs:
                params["file_ids"] = kwargs["file_ids"]
            
            # Fazer requisição para executar o agente
            response = self._make_request(
                method="POST", 
                endpoint=f"agents/{agent_id}/execute",
                json=params
            )
            
            logger.info(f"Agente {agent_id} executado com sucesso")
            return response
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.error(f"Agente não encontrado: {agent_id}")
                raise ValueError(f"Agente não encontrado: {agent_id}")
            else:
                logger.error(f"Erro HTTP ao executar agente {agent_id}: {e}")
                raise RuntimeError(f"Falha ao executar agente: {str(e)}")
        except Exception as e:
            logger.error(f"Erro ao executar agente {agent_id}: {e}")
            raise RuntimeError(f"Falha ao executar agente: {str(e)}")
    
    def upload_file(self, file_path: str, process: bool = False) -> Dict[str, Any]:
        """
        Faz upload de um arquivo para o TESS.
        
        Args:
            file_path: Caminho do arquivo a ser enviado
            process: Se o arquivo deve ser processado após o upload
            
        Returns:
            Dict[str, Any]: Informações sobre o arquivo enviado
            
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado
            RuntimeError: Se houver erro no upload
        """
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
            
            # Preparar multipart/form-data
            files = {"file": open(file_path, "rb")}
            data = {"process": "true" if process else "false"}
            
            # Fazer requisição para upload do arquivo
            response = self._make_request(
                method="POST",
                endpoint="files",
                files=files,
                data=data
            )
            
            logger.info(f"Arquivo {file_path} enviado com sucesso para o TESS")
            return response
            
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Erro ao fazer upload do arquivo {file_path}: {e}")
            raise RuntimeError(f"Falha ao fazer upload do arquivo: {str(e)}")
    
    # Implementações de outros métodos da interface... 