"""
Adaptador para o servidor MCP FastAPI.
"""

import os
import signal
import subprocess
import time
import requests
import json
import logging
from typing import Dict, Any, List, Optional
import threading

from domain.interfaces.mcp_server import MCPServerInterface

logger = logging.getLogger(__name__)


class FastAPIMCPServerAdapter(MCPServerInterface):
    """
    Adaptador para o servidor MCP baseado em FastAPI.
    
    Esta classe implementa a interface MCPServerInterface para
    o servidor MCP implementado em FastAPI.
    """
    
    def __init__(self, 
                 server_path: str = None,
                 host: str = "localhost", 
                 port: int = 8000,
                 auto_start: bool = False):
        """
        Inicializa o adaptador para o servidor MCP FastAPI.
        
        Args:
            server_path (str, optional): Caminho para o arquivo do servidor FastAPI.
                                       Se não for fornecido, usa o caminho padrão.
            host (str, optional): Host onde o servidor estará rodando. Padrão é "localhost".
            port (int, optional): Porta onde o servidor estará rodando. Padrão é 8000.
            auto_start (bool, optional): Se deve iniciar o servidor automaticamente. Padrão é False.
        """
        self.host = host
        self.port = port
        
        # Define o caminho do servidor
        if server_path is None:
            # Caminho padrão relativo à raiz do projeto
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.server_path = os.path.join(base_dir, "hybrid_mcp", "fastapi_server.py")
        else:
            self.server_path = server_path
        
        # Verifica se o arquivo existe
        if not os.path.isfile(self.server_path):
            raise FileNotFoundError(f"Arquivo do servidor FastAPI não encontrado em: {self.server_path}")
        
        self.base_url = f"http://{host}:{port}"
        self.process = None
        self.running = False
        
        # Inicia o servidor se auto_start for True
        if auto_start:
            self.start()
    
    def start(self) -> bool:
        """
        Inicia o servidor MCP FastAPI.
        
        Returns:
            bool: True se o servidor foi iniciado com sucesso, False caso contrário.
        """
        if self.running:
            logger.info("Servidor já está em execução")
            return True
        
        try:
            # Inicia o servidor em um processo separado
            cmd = ["python", self.server_path]
            self.process = subprocess.Popen(
                cmd,
                env=os.environ.copy(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Espera o servidor iniciar
            logger.info(f"Iniciando servidor FastAPI MCP em {self.base_url}")
            time.sleep(2)  # Tempo para o servidor iniciar
            
            # Verifica se o servidor está respondendo
            if self.health_check():
                self.running = True
                logger.info("Servidor FastAPI MCP iniciado com sucesso")
                return True
            else:
                logger.error("Falha ao iniciar o servidor FastAPI MCP")
                self.stop()
                return False
                
        except Exception as e:
            logger.error(f"Erro ao iniciar servidor FastAPI MCP: {str(e)}")
            if self.process:
                self.stop()
            return False
    
    def stop(self) -> bool:
        """
        Para o servidor MCP.
        
        Returns:
            bool: True se o servidor foi parado com sucesso, False caso contrário.
        """
        if not self.running or not self.process:
            logger.info("Servidor não está em execução")
            self.running = False
            return True
        
        try:
            # Envia sinal para encerrar o processo
            os.kill(self.process.pid, signal.SIGTERM)
            
            # Espera o processo encerrar
            self.process.wait(timeout=5)
            self.running = False
            logger.info("Servidor FastAPI MCP parado com sucesso")
            return True
        except subprocess.TimeoutExpired:
            # Força o encerramento se não terminar normalmente
            logger.warning("Timeout ao parar servidor, forçando encerramento")
            os.kill(self.process.pid, signal.SIGKILL)
            self.running = False
            return True
        except Exception as e:
            logger.error(f"Erro ao parar servidor FastAPI MCP: {str(e)}")
            return False
    
    def get_status(self) -> str:
        """
        Retorna o status atual do servidor.
        
        Returns:
            str: O status do servidor ("running", "stopped", "error").
        """
        if not self.running:
            return "stopped"
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            if response.status_code == 200:
                return "running"
            else:
                return "error"
        except Exception:
            return "error"
    
    def get_endpoint(self) -> str:
        """
        Retorna o endpoint principal do servidor.
        
        Returns:
            str: A URL do endpoint principal.
        """
        return f"{self.base_url}/api/mcp"
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        Lista todas as ferramentas disponíveis no servidor.
        
        Returns:
            List[Dict[str, Any]]: Lista de ferramentas com seus metadados.
            
        Raises:
            RuntimeError: Se o servidor não estiver em execução ou ocorrer um erro.
        """
        if not self.running:
            raise RuntimeError("Servidor não está em execução. Use start() para iniciá-lo.")
        
        try:
            response = requests.get(f"{self.base_url}/api/mcp/tools", timeout=5)
            if response.status_code == 200:
                return response.json()["tools"]
            else:
                raise RuntimeError(f"Erro ao listar ferramentas: {response.status_code} - {response.text}")
        except Exception as e:
            raise RuntimeError(f"Erro ao listar ferramentas: {str(e)}")
    
    def execute_tool(self, tool_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma ferramenta específica no servidor.
        
        Args:
            tool_id (str): Identificador da ferramenta.
            params (Dict[str, Any]): Parâmetros para a execução da ferramenta.
            
        Returns:
            Dict[str, Any]: Resultado da execução da ferramenta.
            
        Raises:
            RuntimeError: Se o servidor não estiver em execução ou ocorrer um erro.
        """
        if not self.running:
            raise RuntimeError("Servidor não está em execução. Use start() para iniciá-lo.")
        
        try:
            data = {
                "name": tool_id,
                "params": params
            }
            response = requests.post(
                f"{self.base_url}/api/mcp/execute",
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise RuntimeError(f"Erro ao executar ferramenta: {response.status_code} - {response.text}")
        except Exception as e:
            raise RuntimeError(f"Erro ao executar ferramenta: {str(e)}")
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Retorna informações sobre o servidor.
        
        Returns:
            Dict[str, Any]: Informações do servidor (versão, capacidades, etc).
        """
        return {
            "type": "FastAPI MCP Server",
            "version": "1.0.0",
            "host": self.host,
            "port": self.port,
            "endpoint": self.get_endpoint(),
            "status": self.get_status(),
            "implementation": "Python/FastAPI",
            "capabilities": ["health_check", "search_info", "process_image", "chat_completion", 
                            "list_agents", "get_agent", "execute_agent", "list_agent_files"]
        }
    
    def health_check(self) -> bool:
        """
        Verifica se o servidor está respondendo corretamente.
        
        Returns:
            bool: True se o servidor está saudável, False caso contrário.
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except Exception:
            return False 