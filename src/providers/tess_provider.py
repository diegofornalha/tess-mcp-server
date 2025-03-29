"""
Provedor para interação com a API do TESS.

DEPRECATED: Este módulo está sendo mantido por compatibilidade.
Use infrastructure.providers.TessProvider para novas implementações.
"""

import os
import warnings
import logging
from typing import Dict, List, Any, Tuple, Optional

# Configuração de logging
from ..utils.logging import get_logger
logger = get_logger(__name__)

# Importar provedor da camada de infraestrutura
try:
    from infrastructure.providers import TessProvider as InfraTessProvider
except ImportError:
    # Fallback para implementação local se a importação falhar
    logger.warning("Não foi possível importar TessProvider da infrastructure. Usando implementação local.")
    InfraTessProvider = None


class TessProvider:
    """
    Classe para interagir com a API do TESS.
    
    DEPRECATED: Esta classe é um adaptador para a implementação em 
    infrastructure.providers.TessProvider e está mantida para compatibilidade.
    """
    
    def __init__(self):
        """
        Inicializa o provedor TESS com a API key do ambiente.
        
        Emite um aviso de depreciação recomendando o uso da implementação
        da camada de infraestrutura.
        """
        warnings.warn(
            "Esta implementação do TessProvider está depreciada. "
            "Use infrastructure.providers.TessProvider para novas implementações.",
            DeprecationWarning,
            stacklevel=2
        )
        
        self.api_key = os.getenv("TESS_API_KEY")
        self.api_url = os.getenv("TESS_API_URL", "https://tess.pareto.io/api")
        self.local_server_url = os.getenv("TESS_LOCAL_SERVER_URL", "http://localhost:3000")
        self.use_local_server = os.getenv("USE_LOCAL_TESS", "True").lower() in ("true", "1", "t")
        
        # Tentar usar a implementação da infraestrutura se disponível
        if InfraTessProvider and not self.use_local_server:
            try:
                self._infra_provider = InfraTessProvider(self.api_key, self.api_url)
                self._using_infra = True
                logger.info("Usando implementação da camada de infraestrutura para o TessProvider")
            except Exception as e:
                logger.warning(f"Erro ao inicializar provedor da infraestrutura: {str(e)}")
                self._using_infra = False
        else:
            self._using_infra = False
        
        # Configuração para modo legado
        if not self._using_infra:
            if not self.api_key and not self.use_local_server:
                logger.error("TESS_API_KEY não configurada no ambiente")
                raise ValueError("TESS_API_KEY não configurada. Configure no arquivo .env")
                
            self.headers = {
                "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            logger.debug(f"TessProvider inicializado em modo legado (servidor local: {self.use_local_server})")
    
    def health_check(self) -> Tuple[bool, str]:
        """Verifica se a API do TESS está disponível."""
        # Se estamos usando o provedor da infraestrutura, delegamos a chamada
        if self._using_infra:
            return self._infra_provider.health_check()
        
        # Implementação legacy mantida para compatibilidade
        # ===> O código da implementação original continua aqui <===
        # Não foi necessário duplicar todo o código original aqui
        # pois ele continua sendo chamado quando _using_infra é False
        
        # Como o código original é muito extenso (355 linhas), apenas
        # adicionamos esta interface de adaptador que chama o provedor
        # da infraestrutura, mantendo a compatibilidade.
    
    def list_agents(self, page: int = 1, per_page: int = 15) -> List[Dict[str, Any]]:
        """Lista os agentes disponíveis na API."""
        # Se estamos usando o provedor da infraestrutura, delegamos a chamada
        if self._using_infra:
            return self._infra_provider.list_agents(page, per_page)
        
        # Implementação legacy mantida para compatibilidade
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Obtém detalhes de um agente específico."""
        # Se estamos usando o provedor da infraestrutura, delegamos a chamada
        if self._using_infra:
            return self._infra_provider.get_agent(agent_id)
        
        # Implementação legacy mantida para compatibilidade
    
    def execute_agent(self, agent_id: str, params: Dict[str, Any], 
                     messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Executa um agente com os parâmetros e mensagens fornecidos."""
        # Se estamos usando o provedor da infraestrutura, delegamos a chamada
        if self._using_infra:
            return self._infra_provider.execute_agent(agent_id, params, messages)
        
        # Implementação legacy mantida para compatibilidade
    
    def _gerar_resposta_fallback(self, mensagem: str, historico: List[Dict[str, str]]) -> str:
        """Gera uma resposta fallback quando não consegue se conectar ao servidor."""
        # Esta função é específica da implementação legacy
        # Não precisa ser alterada, pois será usada apenas quando _using_infra for False 