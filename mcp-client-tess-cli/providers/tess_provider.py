import os
import requests
import json
from typing import Dict, List, Optional, Tuple, Any
import logging
from domain.interfaces import TessProviderInterface

logger = logging.getLogger(__name__)

class TessProvider(TessProviderInterface):
    """
    Implementação concreta do provedor TESS que segue a interface definida no domínio.
    """
    
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None):
        """
        Inicializa o provedor TESS com as credenciais fornecidas.
        
        Args:
            api_key: Chave de API para o serviço TESS (opcional, usará variável de ambiente se None)
            api_url: URL base da API TESS (opcional, usará variável de ambiente se None)
        """
        self.api_key = api_key or os.getenv("TESS_API_KEY")
        self.api_url = api_url or os.getenv("TESS_API_URL", "https://tess.pareto.io/api")
        
        if not self.api_key:
            raise ValueError("TESS_API_KEY não configurada")
        
        if not self.api_url:
            raise ValueError("TESS_API_URL não configurada")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def health_check(self) -> Tuple[bool, str]:
        """
        Verifica a conexão com a API TESS tentando listar agentes.
        
        Returns:
            Tuple[bool, str]: Tupla contendo status (True/False) e mensagem.
        """
        try:
            response = requests.get(
                f"{self.api_url}/agents",
                params={"page": 1, "per_page": 1},
                headers=self.headers
            )
            
            if response.status_code == 401:
                return False, "Erro de autenticação: verifique sua TESS_API_KEY"
            
            response.raise_for_status()
            return True, "Conexão com TESS API estabelecida com sucesso"
            
        except requests.exceptions.ConnectionError:
            return False, "Erro de conexão: não foi possível conectar ao servidor TESS"
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao verificar conexão com TESS API: {str(e)}")
            return False, f"Erro ao conectar com TESS API: {str(e)}"

    def list_agents(self, page: int = 1, per_page: int = 15, filter_type: str = None, keyword: str = None) -> List[Dict]:
        """
        Lista os agentes disponíveis no serviço TESS.
        
        Args:
            page: Número da página para paginação
            per_page: Número de itens por página
            filter_type: Filtrar por tipo de agente (ex: 'chat', 'completion', etc.)
            keyword: Filtrar por palavra-chave no título ou descrição
            
        Returns:
            List[Dict]: Lista de agentes disponíveis
        """
        try:
            params = {
                "page": page,
                "per_page": per_page
            }
            
            # Adicionar tipo ao parâmetro se especificado
            if filter_type:
                params['type'] = filter_type
                
            response = requests.get(
                f"{self.api_url}/agents",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            
            # Obter a resposta como JSON
            data = response.json()
            
            # Transformar a resposta em uma lista de dicionários com formato padronizado
            agents = []
            for agent in data.get('data', []):
                agent_info = {
                    'id': agent.get('id'),
                    'name': agent.get('title', ''),
                    'description': agent.get('description', ''),
                    'type': agent.get('type', ''),
                    'slug': agent.get('slug', '')
                }
                agents.append(agent_info)
            
            # Filtragem adicional de tipo - caso a API não suporte filtro por tipo no parâmetro
            if filter_type:
                original_count = len(agents)
                agents = [agent for agent in agents if agent.get('type', '').lower() == filter_type.lower()]
                filtered_count = len(agents)
                logger.debug(f"Filtro adicional por tipo '{filter_type}': {filtered_count} de {original_count} agentes")
            
            # Filtragem adicional por palavra-chave
            if keyword:
                agents = self._filter_agents_by_keyword(agents, keyword)
                
            return agents
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao listar agentes: {str(e)}")
            return []

    def _filter_agents_by_keyword(self, agents: List[Dict], keyword: str) -> List[Dict]:
        """
        Filtra agentes por palavra-chave no nome, descrição ou ID.
        
        Args:
            agents: Lista de agentes para filtrar
            keyword: Palavra-chave para busca
            
        Returns:
            List[Dict]: Lista filtrada de agentes
        """
        if not keyword:
            return agents
            
        keyword_lower = keyword.lower()
        original_count = len(agents)
        filtered_agents = []
        
        for agent in agents:
            name = agent.get('name', '').lower()
            description = agent.get('description', '').lower()
            agent_id = str(agent.get('id', '')).lower()
            slug = str(agent.get('slug', '')).lower()
            
            if (keyword_lower in name or 
                keyword_lower in description or 
                keyword_lower in agent_id or
                keyword_lower in slug):
                filtered_agents.append(agent)
        
        logger.debug(f"Filtro por palavra-chave '{keyword}': {len(filtered_agents)} de {original_count} agentes")
        return filtered_agents

    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """
        Obtém detalhes de um agente específico.
        
        Args:
            agent_id: Identificador do agente a ser consultado
            
        Returns:
            Optional[Dict]: Detalhes do agente ou None se não encontrado
        """
        try:
            response = requests.get(
                f"{self.api_url}/agents/{agent_id}",
                headers=self.headers
            )
            response.raise_for_status()
            
            agent = response.json()
            return {
                'id': agent.get('id'),
                'name': agent.get('title'),
                'description': agent.get('description', ''),
                'type': agent.get('type', ''),
                'visibility': agent.get('visibility', ''),
                'questions': agent.get('questions', []),
                'slug': agent.get('slug', '')
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter agente {agent_id}: {str(e)}")
            return None
            
    def execute_agent(self, agent_id: str, params: Dict[str, Any], messages: List[Dict[str, str]]) -> Dict:
        """
        Executa um agente com os parâmetros fornecidos e mensagens.

        Args:
            agent_id: ID do agente a ser executado
            params: Dicionário com os parâmetros do agente
            messages: Lista de mensagens no formato [{role: "user", content: "mensagem"}]

        Returns:
            Dict: Resposta da execução do agente
        """
        try:
            # Para a API TESS, precisamos extrair a última mensagem do usuário
            # e usá-la como entrada para o agente
            last_user_message = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_user_message = msg.get("content", "")
                    break
                    
            if not last_user_message:
                raise ValueError("Nenhuma mensagem do usuário encontrada no histórico")
            
            # Verificar se estamos no modo auto
            using_auto_mode = params.get("model") == "auto"
            if using_auto_mode:
                logger.info("Usando modo AUTO para seleção dinâmica de modelo")
            
            # Preparar dados para a requisição
            # Na API TESS, enviamos o conteúdo do prompt diretamente
            payload = {
                **params,  # Parâmetros do agente (nome-empresa, etc)
                "prompt": last_user_message  # A última mensagem do usuário é o prompt
            }
            
            # Adicionar parâmetros específicos para o modo auto
            if using_auto_mode:
                payload["return_model_info"] = True
            
            logger.debug(f"Executando agente {agent_id} com payload: {json.dumps(payload)}")
            
            # Executar o agente
            # O endpoint correto é /agents/{id}/execute 
            response = requests.post(
                f"{self.api_url}/agents/{agent_id}/execute",
                headers=self.headers,
                json=payload,
                timeout=60  # Aumentando o timeout para evitar erros por demora na resposta
            )
            
            if response.status_code == 401:
                raise ValueError("Erro de autenticação: verifique sua TESS_API_KEY")
            
            if response.status_code == 404:
                raise ValueError(f"Agente com ID {agent_id} não encontrado")
                
            response.raise_for_status()
            
            response_data = response.json()
            logger.debug(f"Resposta do agente: {json.dumps(response_data)}")
            
            # Extrair informações sobre o modelo usado (quando no modo auto)
            model_used = response_data.get("model_used", None) or params.get("model", "desconhecido")
            
            if using_auto_mode and model_used:
                logger.info(f"Modo AUTO selecionou o modelo: {model_used}")
            
            # Retornar o formato compatível com o esperado pelo chat
            # Na API TESS, a resposta está no campo 'response'
            return {
                'content': response_data.get('response', 'Sem resposta do assistente'),
                'role': 'assistant',
                'agent_id': agent_id,
                'model': model_used
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao executar agente {agent_id}: {str(e)}")
            # Tentar novamente com timeout maior apenas para erros de timeout
            if "timeout" in str(e).lower():
                try:
                    logger.info(f"Tentando novamente com timeout maior para agente {agent_id}")
                    response = requests.post(
                        f"{self.api_url}/agents/{agent_id}/execute",
                        headers=self.headers,
                        json=payload,
                        timeout=120  # Timeout ainda maior para segunda tentativa
                    )
                    response.raise_for_status()
                    
                    response_data = response.json()
                    model_used = response_data.get("model_used", None) or params.get("model", "desconhecido")
                    
                    return {
                        'content': response_data.get('response', 'Sem resposta do assistente'),
                        'role': 'assistant',
                        'agent_id': agent_id,
                        'model': model_used
                    }
                except Exception as retry_error:
                    logger.error(f"Segunda tentativa falhou para agente {agent_id}: {str(retry_error)}")
            
            raise ValueError(f"Erro ao executar agente: {str(e)}") 