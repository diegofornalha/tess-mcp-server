"""
Adaptador para o servidor MCP Node.js/WebAssembly.
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


class NodeJsWasmMCPServerAdapter(MCPServerInterface):
    """
    Adaptador para o servidor MCP baseado em Node.js e WebAssembly.
    
    Esta classe implementa a interface MCPServerInterface para
    o servidor MCP implementado em Node.js com plugin WebAssembly.
    """
    
    def __init__(self, 
                 server_dir: str = None,
                 host: str = "localhost", 
                 port: int = 3000,
                 auto_start: bool = False):
        """
        Inicializa o adaptador para o servidor MCP Node.js/WebAssembly.
        
        Args:
            server_dir (str, optional): Diretório do servidor Node.js.
                                      Se não for fornecido, usa o caminho padrão.
            host (str, optional): Host onde o servidor estará rodando. Padrão é "localhost".
            port (int, optional): Porta onde o servidor estará rodando. Padrão é 3000.
            auto_start (bool, optional): Se deve iniciar o servidor automaticamente. Padrão é False.
        """
        self.host = host
        self.port = port
        
        # Define o diretório do servidor
        if server_dir is None:
            # Caminho padrão relativo à raiz do projeto
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.server_dir = os.path.join(base_dir, "mcp-server-tess-xtp")
        else:
            self.server_dir = server_dir
        
        # Verifica se o diretório existe
        if not os.path.isdir(self.server_dir):
            raise FileNotFoundError(f"Diretório do servidor Node.js não encontrado em: {self.server_dir}")
        
        # Verifica se o arquivo server.js existe
        self.server_path = os.path.join(self.server_dir, "server.js")
        if not os.path.isfile(self.server_path):
            raise FileNotFoundError(f"Arquivo server.js não encontrado em: {self.server_path}")
        
        self.base_url = f"http://{host}:{port}"
        self.process = None
        self.running = False
        
        # Define variáveis de ambiente
        self.env = os.environ.copy()
        self.env["PORT"] = str(port)
        
        # Inicia o servidor se auto_start for True
        if auto_start:
            self.start()
    
    def start(self) -> bool:
        """
        Inicia o servidor MCP Node.js/WebAssembly.
        
        Returns:
            bool: True se o servidor foi iniciado com sucesso, False caso contrário.
        """
        if self.running:
            logger.info("Servidor já está em execução")
            return True
        
        try:
            # Muda para o diretório do servidor
            current_dir = os.getcwd()
            os.chdir(self.server_dir)
            
            # Inicia o servidor em um processo separado
            cmd = ["node", "server.js"]
            self.process = subprocess.Popen(
                cmd,
                env=self.env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Volta para o diretório original
            os.chdir(current_dir)
            
            # Espera o servidor iniciar
            logger.info(f"Iniciando servidor Node.js/WebAssembly MCP em {self.base_url}")
            time.sleep(5)  # Tempo maior para o servidor Node.js iniciar
            
            # Verifica se o servidor está respondendo
            if self.health_check():
                self.running = True
                logger.info("Servidor Node.js/WebAssembly MCP iniciado com sucesso")
                return True
            else:
                logger.error("Falha ao iniciar o servidor Node.js/WebAssembly MCP")
                self.stop()
                return False
                
        except Exception as e:
            logger.error(f"Erro ao iniciar servidor Node.js/WebAssembly MCP: {str(e)}")
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
            logger.info("Servidor Node.js/WebAssembly MCP parado com sucesso")
            return True
        except subprocess.TimeoutExpired:
            # Força o encerramento se não terminar normalmente
            logger.warning("Timeout ao parar servidor, forçando encerramento")
            os.kill(self.process.pid, signal.SIGKILL)
            self.running = False
            return True
        except Exception as e:
            logger.error(f"Erro ao parar servidor Node.js/WebAssembly MCP: {str(e)}")
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
                return json.loads(response.text)["tools"]
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
                return json.loads(response.text)
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
            "type": "Node.js/WebAssembly MCP Server",
            "version": "1.0.0",
            "host": self.host,
            "port": self.port,
            "endpoint": self.get_endpoint(),
            "status": self.get_status(),
            "implementation": "Node.js/WebAssembly",
            "features": ["Proxy MCP", "WebAssembly Plugin", "Rust Backend"]
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