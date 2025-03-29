#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implementação do provider para o serviço Arcee AI.

O Arcee AI é uma plataforma que oferece soluções de IA, incluindo:
- Arcee Orchestra: plataforma agentic para construir fluxos de trabalho de IA
- Arcee Conductor: roteador inteligente que seleciona o modelo mais adequado e 
  eficiente em custo para cada prompt
- Small Language Models (SLMs): modelos de linguagem menores otimizados para
  tarefas específicas

Este módulo implementa a interface para comunicação com os serviços Arcee AI,
principalmente para geração de conteúdo e chat.
"""

import os
import time
import json
import logging
from typing import Dict, List, Tuple, Union, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
from domain.interfaces import ArceeProviderInterface

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do logger
logger = logging.getLogger(__name__)

class ArceeProvider(ArceeProviderInterface):
    """Provedor de serviços do Arcee AI que implementa a interface definida no domínio."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Inicializa o provedor
        
        Args:
            api_key: Chave de API para a Arcee AI (opcional)
            model: Modelo padrão a ser usado (opcional)
        """
        # INVERSÃO DE PRIORIDADE: Agora prioriza a configuração sobre as variáveis de ambiente
        # Primeiro verifica se foi passada uma chave
        self.api_key = api_key

        # Se não tiver sido passada, tenta carregar do arquivo de configuração
        if not self.api_key:
            self.api_key = self._load_api_key_from_config()

        # Se não encontrou na configuração, tenta das variáveis de ambiente
        if not self.api_key:
            self.api_key = os.getenv("ARCEE_API_KEY")

        if not self.api_key:
            raise ValueError(
                "API key não encontrada. Defina ARCEE_API_KEY no .env ou configure com 'arcee config --api-key'."
            )

        self.model = model or os.getenv("ARCEE_MODEL") or "auto"
        
        # Rastreamento de modelos
        self.last_model_used = None
        self.model_usage_stats = {}

        # Templates de mensagem do sistema para diferentes contextos
        self.system_templates = {
            "default": "Você deve sempre responder em português do Brasil. Use uma linguagem natural e informal, mas profissional. Suas respostas devem ser claras, objetivas e culturalmente adequadas para o Brasil.",
            "technical": "Você deve sempre responder em português do Brasil. Para questões técnicas, forneça explicações detalhadas com exemplos práticos quando possível. Mantenha uma linguagem técnica apropriada.",
            "creative": "Você deve sempre responder em português do Brasil. Para tarefas criativas, seja imaginativo e ofereça múltiplas opções. Use uma linguagem expressiva e envolvente."
        }
    
        # Configura o cliente OpenAI
        self.client = OpenAI(
            api_key=self.api_key, 
            base_url="https://models.arcee.ai/v1",
        )
        
        logger.debug("ArceeProvider inicializado com sucesso")

    def _load_api_key_from_config(self) -> str:
        """
        Carrega a chave API do arquivo de configuração
        
        Returns:
            str: Chave API encontrada ou string vazia
        """
        # Primeiro tenta na nova localização
        config_file = os.path.expanduser("~/.tess/arcee_config.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    api_key = config.get("api_key", "")
                    if api_key:
                        logger.info("Chave API carregada da configuração")
                        return api_key
            except Exception as e:
                logger.error(f"Erro ao carregar nova configuração: {str(e)}")
        
        # Se não encontrou, tenta na localização legada
        legacy_config = os.path.expanduser("~/.arcee/config.json")
        if os.path.exists(legacy_config):
            try:
                with open(legacy_config, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    api_key = config.get("api_key", "")
                    if api_key:
                        logger.info("Chave API carregada da configuração legada")
                        # Migra para nova localização
                        self._save_api_key_to_config(api_key)
                        return api_key
            except Exception as e:
                logger.error(f"Erro ao carregar configuração legada: {str(e)}")
                
        return ""
    
    def _save_api_key_to_config(self, api_key: str) -> bool:
        """
        Salva a chave API no arquivo de configuração
        
        Args:
            api_key: Chave API a ser salva
            
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        try:
            # Cria o diretório de configuração se não existir
            config_dir = os.path.expanduser("~/.tess")
            os.makedirs(config_dir, exist_ok=True)
            
            config_file = os.path.join(config_dir, "arcee_config.json")
            
            # Lê a configuração existente, se houver
            config = {}
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
            
            # Atualiza a chave API
            config["api_key"] = api_key
            
            # Salva a configuração
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
                
            logger.info("Chave API salva na configuração")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {str(e)}")
            return False
            
    def _select_system_template(self, messages: List[Dict[str, str]]) -> str:
        """
        Seleciona o template de sistema mais adequado com base nas mensagens
        
        Args:
            messages: Lista de mensagens da conversa
            
        Returns:
            str: Conteúdo do template de sistema selecionado
        """
        # Verifica últimas mensagens do usuário para entender o contexto
        last_user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "").lower()
                break
        
        # Palavras-chave para identificar contexto técnico
        technical_keywords = [
            "código", "programação", "função", "classe", "método", 
            "compilar", "debug", "erro", "algoritmo", "framework",
            "biblioteca", "api", "desenvolvimento", "software", "script",
            "implementar", "python", "javascript", "java", "c++", "html",
            "css", "sql", "bash", "terminal", "linux", "git"
        ]
        
        # Palavras-chave para identificar contexto criativo
        creative_keywords = [
            "criativo", "ideia", "gerar", "criar", "inventar", "imaginar",
            "design", "arte", "música", "poesia", "história", "narrativa",
            "criação", "escrever", "conteúdo", "marketing", "brainstorm",
            "inspiração", "conceito", "inovação", "original"
        ]
        
        # Verificar contexto técnico
        for keyword in technical_keywords:
            if keyword in last_user_message:
                logger.debug("Contexto técnico identificado")
                return self.system_templates["technical"]
                
        # Verificar contexto criativo
        for keyword in creative_keywords:
            if keyword in last_user_message:
                logger.debug("Contexto criativo identificado")
                return self.system_templates["creative"]
        
        # Se não identificar um contexto específico, usa o template padrão
        return self.system_templates["default"]

    def health_check(self) -> Dict[str, Any]:
        """
        Verifica a saúde da API
        
        Returns:
            Dict[str, Any]: Resultado da verificação de saúde
        """
        try:
            # Apenas verifica se temos uma chave API configurada
            if not self.api_key:
                return {
                    "status": "error",
                    "message": "Chave API não configurada"
                }
                
            # Tenta uma requisição simples para verificar a conectividade
            try:
                self.client.models.list()
                return {
                    "status": "success",
                    "message": "Conexão com API Arcee estabelecida com sucesso"
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Erro ao conectar com API Arcee: {str(e)}"
                }
                
        except Exception as e:
            logger.error(f"Erro ao verificar configuração: {str(e)}")
            return {
                "status": "error",
                "message": f"Erro ao verificar configuração: {str(e)}"
            }

    def generate_content_chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Gera conteúdo usando o chat com seleção automática de modelo e template
        
        Args:
            messages: Lista de mensagens no formato [{role: "user", content: "mensagem"}]
            model: Modelo a ser utilizado (opcional, usa o padrão se None)
            system_prompt: Prompt de sistema (opcional)
            context: Contexto adicional (opcional)
            temperature: Temperatura para geração (criatividade)
            **kwargs: Argumentos adicionais para a API
            
        Returns:
            Dict[str, Any]: Resposta com o conteúdo gerado
        """
        try:
            if not self.api_key:
                return {"error": "Chave API não configurada"}

            # Registra apenas o tempo inicial
            start_time = time.time()
            
            # Define o modelo a ser usado
            modelo_efetivo = model or self.model
            
            # Seleciona o template de sistema apropriado com base no contexto
            system_content = system_prompt or self._select_system_template(messages)
            
            # Cria uma cópia das mensagens para não modificar a original
            processed_messages = messages.copy()
            
            # Adiciona ou atualiza a mensagem do sistema
            if not processed_messages or processed_messages[0].get("role") != "system":
                processed_messages = [{"role": "system", "content": system_content}] + processed_messages
            else:
                # Atualiza a mensagem de sistema existente
                processed_messages[0]["content"] = system_content

            # Parâmetros adicionais para o modo auto
            extra_params = {}
            if modelo_efetivo == "auto":
                # Pode incluir parâmetros específicos para o modo auto
                # como solicitação de metadados sobre o modelo selecionado
                extra_params = {}
                logger.info("Usando modo AUTO para seleção dinâmica de modelo")

            # Faz a requisição usando o cliente OpenAI
            response = self.client.chat.completions.create(
                model=modelo_efetivo,
                messages=processed_messages,
                temperature=temperature,
                **extra_params
            )

            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.debug(f"Tempo de resposta da API: {elapsed_time:.2f} segundos")

            # Processa e retorna a resposta
            return self._process_response(response)

        except Exception as e:
            logger.error(f"Erro na chamada à API da Arcee: {e}")
            return {"error": str(e)}

    def _process_response(self, response) -> Dict[str, Any]:
        """
        Processa a resposta da API da Arcee

        Args:
            response: Resposta do cliente OpenAI

        Returns:
            Dict[str, Any]: Resposta processada
        """
        try:
            # Extrai o texto da resposta
            content = response.choices[0].message.content

            # Obtém metadados da resposta
            finish_reason = response.choices[0].finish_reason
            model_used = response.model
            
            # Rastreia o modelo usado para análise e ajustes futuros
            self.last_model_used = model_used
            
            # Atualiza estatísticas de uso do modelo
            if model_used in self.model_usage_stats:
                self.model_usage_stats[model_used] += 1
            else:
                self.model_usage_stats[model_used] = 1
                
            # Log do modelo selecionado para depuração
            if self.model == "auto":
                logger.info(f"Modo AUTO selecionou o modelo: {model_used}")

            # Formata a resposta
            processed_response = {
                "text": content,
                "finish_reason": finish_reason,
                "model": model_used,
                "usage": {
                    "total_tokens": getattr(response.usage, "total_tokens", 0),
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(response.usage, "completion_tokens", 0)
                }
            }

            return processed_response
        except Exception as e:
            logger.error(f"Erro ao processar resposta: {e}")
            return {"error": str(e)}

    def chat(
        self, 
        message: str, 
        history: Optional[List[Dict[str, str]]] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Realiza uma interação de chat simples
        
        Args:
            message: Mensagem do usuário
            history: Histórico de mensagens anteriores (opcional)
            model: Modelo a ser usado (opcional)
            system_prompt: Prompt de sistema (opcional)
            **kwargs: Argumentos adicionais
            
        Returns:
            Dict[str, Any]: Resposta do chat
        """
        if history is None:
            history = []
            
        # Adiciona a mensagem atual ao histórico
        mensagens = history + [{"role": "user", "content": message}]
        
        # Gera a resposta
        resultado = self.generate_content_chat(
            messages=mensagens,
            model=model,
            system_prompt=system_prompt,
            **kwargs
        )
        
        if "error" in resultado:
            return {
                "content": f"Erro: {resultado['error']}",
                "success": False,
                "error": resultado["error"],
                "history": mensagens
            }
            
        # Adiciona a resposta ao histórico para contexto futuro
        mensagens.append({"role": "assistant", "content": resultado["text"]})
        
        return {
            "content": resultado["text"],
            "success": True,
            "model": resultado.get("model", "desconhecido"),
            "history": mensagens
        }
    
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de modelos disponíveis
        
        Returns:
            List[Dict[str, Any]]: Lista de modelos disponíveis
        """
        try:
            response = self.client.models.list()
            models = []
            
            for model in response.data:
                models.append({
                    "id": model.id,
                    "created": model.created,
                    "owned_by": model.owned_by
                })
                
            return models
        except Exception as e:
            logger.error(f"Erro ao obter modelos: {e}")
            return []
    
    def set_model(self, model: str) -> bool:
        """
        Define o modelo padrão para uso
        
        Args:
            model: ID do modelo ou "auto" para seleção automática
            
        Returns:
            bool: True se configurado com sucesso
        """
        self.model = model
        
        # Salva na configuração
        try:
            config_file = os.path.expanduser("~/.tess/arcee_config.json")
            
            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            # Lê a configuração existente
            config = {}
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    
            # Atualiza e salva
            config["model"] = model
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
                
            logger.info(f"Modelo padrão definido para: {model}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar configuração de modelo: {e}")
            return False 