"""
Interfaces para provedores de serviços externos.

Este módulo define as interfaces para provedores que serão implementados
na camada de infraestrutura, seguindo o princípio de inversão de dependência.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple


class TessProviderInterface(ABC):
    """
    Interface para provedores do serviço TESS (Tess AI API).
    
    O TESS é uma plataforma que oferece APIs para integração de agentes de IA
    e capacidades de gerenciamento de arquivos em aplicações. Esta interface
    define os métodos que qualquer implementação de cliente TESS deve fornecer.
    """

    @abstractmethod
    def health_check(self) -> Tuple[bool, str]:
        """
        Verifica a conexão com a API TESS.
        
        Returns:
            Tuple[bool, str]: Status da conexão (True/False) e mensagem explicativa
        """
        pass
    
    @abstractmethod
    def list_agents(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Lista os agentes disponíveis no TESS.
        
        Args:
            filters: Filtros opcionais para a busca (ex: página, quantidade por página)
            
        Returns:
            List[Dict[str, Any]]: Lista de agentes disponíveis
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def execute_agent(self, agent_id: str, input_text: str, **kwargs) -> Dict[str, Any]:
        """
        Executa um agente específico com o texto fornecido.
        
        Args:
            agent_id: ID do agente a ser executado
            input_text: Texto de entrada para o agente
            **kwargs: Parâmetros adicionais para a execução (ex: temperatura, modelo)
            
        Returns:
            Dict[str, Any]: Resultado da execução
            
        Raises:
            ValueError: Se o agente não for encontrado
            RuntimeError: Se houver erro na execução
        """
        pass
    
    @abstractmethod
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
        pass


class MCPProviderInterface(ABC):
    """
    Interface para provedores que implementam o Model Context Protocol (MCP).
    
    O MCP é um protocolo padronizado que permite a comunicação entre modelos de
    linguagem e ferramentas externas. Esta interface define os métodos necessários
    para gerenciar sessões MCP e interagir com ferramentas através do protocolo.
    """
    
    @abstractmethod
    def get_mcp_session_id(self) -> Optional[str]:
        """
        Obtém o ID de sessão do MCP.
        
        Returns:
            Optional[str]: ID de sessão ou None se não configurado.
        """
        pass
    
    @abstractmethod
    def save_mcp_session_id(self, session_id: str) -> bool:
        """
        Salva o ID de sessão do MCP.
        
        Args:
            session_id: ID de sessão a ser salvo.
            
        Returns:
            bool: True se salvou com sucesso, False caso contrário.
        """
        pass
    
    @abstractmethod
    def check_mcp_configured(self) -> bool:
        """
        Verifica se o cliente MCP está configurado corretamente.
        
        Returns:
            bool: True se configurado, False caso contrário.
        """
        pass
    
    @abstractmethod
    def clear_mcp_config(self) -> bool:
        """
        Limpa a configuração do cliente MCP.
        
        Returns:
            bool: True se limpou com sucesso, False caso contrário.
        """
        pass


class ArceeProviderInterface(ABC):
    """
    Interface para provedores de acesso aos serviços Arcee AI.
    
    Arcee AI é uma plataforma que oferece soluções de IA, incluindo:
    - Arcee Orchestra: plataforma agentic para construir fluxos de trabalho de IA
    - Arcee Conductor: roteador inteligente que seleciona o modelo mais adequado e 
      eficiente em custo para cada prompt
    - Small Language Models (SLMs): modelos de linguagem menores otimizados para
      tarefas específicas
    
    Esta interface define os métodos para interagir com os serviços Arcee AI,
    principalmente para geração de conteúdo e chat.
    """
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Verifica a saúde da API Arcee.
        
        Returns:
            Dict[str, Any]: Resultado da verificação de saúde.
        """
        pass
    
    @abstractmethod
    def generate_content_chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Gera conteúdo usando o recurso de chat da Arcee.
        
        Args:
            messages: Lista de mensagens no formato [{"role": "user", "content": "mensagem"}]
            model: Modelo a ser usado (opcional)
            system_prompt: Prompt de sistema (opcional)
            context: Contexto adicional para o prompt (opcional)
            **kwargs: Argumentos adicionais para a API
            
        Returns:
            Dict[str, Any]: Resposta da API Arcee.
        """
        pass
    
    @abstractmethod
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
            message: Mensagem do usuário
            history: Histórico de mensagens anteriores (opcional)
            model: Modelo a ser usado (opcional)
            system_prompt: Prompt de sistema (opcional)
            **kwargs: Argumentos adicionais
            
        Returns:
            Dict[str, Any]: Resposta incluindo o texto gerado e histórico atualizado.
        """
        pass
    
    @abstractmethod
    def get_models(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de modelos disponíveis.
        
        Returns:
            List[Dict[str, Any]]: Lista de modelos disponíveis.
        """
        pass
    
    @abstractmethod
    def set_model(self, model: str) -> bool:
        """
        Define o modelo padrão a ser usado.
        
        Args:
            model: ID do modelo ou "auto" para seleção automática via Arcee Conductor
            
        Returns:
            bool: True se configurado com sucesso, False caso contrário.
        """
        pass


class ProviderFactoryInterface(ABC):
    """Interface para fábrica de provedores."""
    
    @abstractmethod
    def get_provider(self, api_key: Optional[str] = None, 
                    api_url: Optional[str] = None) -> Any:
        """
        Retorna uma instância do provedor padrão.
        
        Args:
            api_key: Chave de API opcional.
            api_url: URL da API opcional.
            
        Returns:
            Any: Instância do provedor.
        """
        pass
    
    @abstractmethod
    def create_provider(self, provider_type: str, api_key: Optional[str] = None, 
                       api_url: Optional[str] = None) -> Any:
        """
        Cria uma instância do provedor especificado.
        
        Args:
            provider_type: Tipo de provedor a ser criado (ex: "tess", "arcee").
            api_key: Chave de API opcional.
            api_url: URL da API opcional.
            
        Returns:
            Any: Instância do provedor solicitado.
        """
        pass 