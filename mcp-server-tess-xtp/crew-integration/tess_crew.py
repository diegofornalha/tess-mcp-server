import os
import json
import logging
import requests
import sys
import subprocess
import time
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from textwrap import dedent

from crewai import Agent, Task, Crew, Process
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    print("Aviso: langchain_openai não está instalado.")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Verificar se arcee está instalado
def check_arcee_installed() -> bool:
    try:
        result = subprocess.run(['arcee', '--version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        return result.returncode == 0
    except Exception:
        return False

class ArceeChatProvider:
    """
    Provedor de chat usando a CLI do Arcee
    """
    def __init__(self):
        self.available = check_arcee_installed()
        if not self.available:
            logger.warning("CLI Arcee não está instalada. Instale com 'pip install arcee-cli'")
    
    def is_available(self) -> bool:
        return self.available
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Envia uma lista de mensagens para o Arcee e retorna a resposta
        """
        if not self.available:
            return "Erro: CLI Arcee não está instalada. Instale com 'pip install arcee-cli'"
        
        try:
            arcee_input = json.dumps(messages)
            result = subprocess.run(['arcee', 'chat'], 
                                   input=arcee_input, 
                                   text=True, 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
            
            if result.returncode != 0:
                logger.error(f"Erro ao executar arcee chat: {result.stderr}")
                return f"Erro ao executar arcee chat: {result.stderr}"
            
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Erro ao executar arcee chat: {str(e)}")
            return f"Erro ao executar arcee chat: {str(e)}"

class OpenAIChatProvider:
    """
    Provedor de chat usando OpenAI
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.available = self.api_key is not None and len(self.api_key) > 0
        if not self.available:
            logger.warning("OPENAI_API_KEY não está configurada.")
    
    def is_available(self) -> bool:
        return self.available
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Envia uma lista de mensagens para a OpenAI e retorna a resposta
        """
        if not self.available:
            return "Erro: OPENAI_API_KEY não está configurada."
        
        try:
            # Use a API da OpenAI
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            data = {
                "model": os.getenv("OPENAI_MODEL", "gpt-4o"),
                "messages": messages
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Erro ao usar a API da OpenAI: {str(e)}")
            return f"Erro ao usar a API da OpenAI: {str(e)}"

class MCPTessTool:
    """
    Wrapper para ferramentas MCP-TESS, permitindo seu uso como ferramentas do CrewAI
    """
    def __init__(self, name, description, parameters=None):
        self.name = name
        self.description = description
        self.parameters = parameters or {}
        
        # Criar uma função dinâmica para esta ferramenta
        self.function = self._create_tool_function()
    
    def _create_tool_function(self):
        """
        Cria uma função dinâmica que representa esta ferramenta
        """
        tool_name = self.name
        tool_parameters = self.parameters
        
        def tool_function(*args, **kwargs):
            """
            Função dinâmica que simula a execução de uma ferramenta TESS
            """
            logger.info(f"Executando ferramenta {tool_name} com parâmetros: {kwargs}")
            
            # Simular respostas para diferentes ferramentas
            if tool_name == "tess.list_agents":
                return {
                    "agents": [
                        {
                            "id": "ag_1",
                            "name": "Assistente de Atendimento",
                            "description": "Responde dúvidas sobre produtos e serviços",
                            "type": "chat"
                        },
                        {
                            "id": "ag_2",
                            "name": "Analista de Dados",
                            "description": "Analisa dados e gera relatórios",
                            "type": "analysis"
                        },
                        {
                            "id": "ag_3",
                            "name": "Pesquisador Web",
                            "description": "Busca informações na internet",
                            "type": "research"
                        }
                    ],
                    "total": 3,
                    "page": kwargs.get("page", 1),
                    "per_page": kwargs.get("per_page", 10)
                }
            
            elif tool_name == "tess.get_agent":
                agent_id = kwargs.get("agent_id")
                return {
                    "id": agent_id,
                    "name": "Agente Simulado",
                    "description": f"Este é um agente simulado com ID {agent_id}",
                    "type": "chat",
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T00:00:00Z"
                }
            
            elif tool_name == "tess.execute_agent":
                agent_id = kwargs.get("agent_id")
                input_text = kwargs.get("input_text", "")
                return {
                    "id": f"ex_{agent_id}_{hash(input_text) % 10000}",
                    "status": "completed",
                    "input": input_text,
                    "output": f"Resposta simulada para: {input_text}",
                    "agent_id": agent_id,
                    "created_at": "2023-01-01T00:00:00Z",
                    "completed_at": "2023-01-01T00:00:01Z"
                }
            
            elif tool_name == "tess.upload_file":
                file_path = kwargs.get("file_path", "")
                return {
                    "id": f"file_{hash(file_path) % 10000}",
                    "name": os.path.basename(file_path),
                    "size": 1024,
                    "mime_type": "text/plain",
                    "created_at": "2023-01-01T00:00:00Z"
                }
            
            elif tool_name == "tess.deep_analysis":
                text = kwargs.get("text", "")
                return {
                    "id": f"analysis_{hash(text) % 10000}",
                    "status": "completed",
                    "result": {
                        "summary": f"Análise profunda do texto: {text[:50]}...",
                        "keywords": ["análise", "profunda", "texto", "TESS"],
                        "sentiment": "positivo",
                        "entities": [
                            {"type": "organization", "text": "Empresa", "confidence": 0.92},
                            {"type": "person", "text": "João Silva", "confidence": 0.85}
                        ]
                    },
                    "created_at": "2023-01-01T00:00:00Z",
                    "completed_at": "2023-01-01T00:00:01Z"
                }
            
            else:
                return {"error": f"Ferramenta {tool_name} não implementada na simulação"}
        
        # Renomear a função para o nome da ferramenta
        tool_function.__name__ = self.name
        tool_function.__doc__ = self.description
        
        return tool_function

class TessCrew:
    """
    Classe principal que gerencia a integração entre CrewAI e MCP-TESS
    """
    def __init__(self):
        self.mcp_base_url = os.getenv("MCP_TESS_HOST", "http://localhost:3001")
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai")
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        
        # Inicializar provedores de chat
        self.arcee_provider = ArceeChatProvider()
        self.openai_provider = OpenAIChatProvider()
        
        # Selecionar provedor conforme configuração
        self.chat_provider = self.arcee_provider if self.arcee_provider.is_available() else self.openai_provider
        llm_provider_name = "arcee" if self.arcee_provider.is_available() else "openai"
        logger.info(f"Usando provedor LLM: {llm_provider_name}")
        
        # Carregar ferramentas TESS simuladas
        self.tess_tools = self.create_tess_tools()
        
        # Inicializar agentes
        self.agents = self._create_agents()
        
        logger.info(f"TessCrew inicializado com {len(self.tess_tools)} ferramentas TESS simuladas")
    
    def create_tess_tools(self) -> List[Dict[str, Any]]:
        """
        Cria ferramentas TESS simuladas para testes
        """
        try:
            # Tentar obter as ferramentas do servidor MCP-TESS
            response = requests.get(f"{self.mcp_base_url}/health", timeout=5)
            if response.status_code != 200:
                logger.warning(f"Erro ao verificar servidor MCP-TESS: código {response.status_code}")
                # Retorna ferramentas simuladas em caso de erro
                return self.create_simulated_tools()
            
            # Se o servidor estiver disponível, obter ferramentas reais
            logger.info("Servidor MCP-TESS disponível. Obtendo ferramentas...")
            
            # Lista de ferramentas simuladas (para estudo e desenvolvimento)
            # Na implementação real, essas ferramentas seriam obtidas do servidor MCP-TESS
            return self.create_simulated_tools()
            
        except Exception as e:
            logger.warning(f"Erro ao conectar ao servidor MCP-TESS: {str(e)}")
            logger.info("Usando ferramentas simuladas em modo offline")
            # Retorna ferramentas simuladas em caso de erro
            return self.create_simulated_tools()
    
    def create_simulated_tools(self) -> List[Dict[str, Any]]:
        """
        Cria ferramentas simuladas para uso em desenvolvimento.
        """
        return [
            {
                "name": "tess.list_agents",
                "description": "Lista os agentes disponíveis na plataforma TESS",
                "parameters": {
                    "page": {
                        "type": "number",
                        "description": "Número da página para paginação",
                        "required": False,
                        "default": 1
                    },
                    "per_page": {
                        "type": "number",
                        "description": "Número de resultados por página",
                        "required": False,
                        "default": 10
                    },
                    "type": {
                        "type": "string",
                        "description": "Tipo de agente para filtragem",
                        "required": False
                    },
                    "q": {
                        "type": "string",
                        "description": "Termo de busca para filtragem por nome",
                        "required": False
                    }
                }
            },
            {
                "name": "tess.get_agent",
                "description": "Obtém detalhes de um agente específico na plataforma TESS",
                "parameters": {
                    "agent_id": {
                        "type": "string",
                        "description": "ID do agente a ser consultado",
                        "required": True
                    }
                }
            },
            {
                "name": "tess.execute_agent",
                "description": "Executa um agente na plataforma TESS com texto de entrada",
                "parameters": {
                    "agent_id": {
                        "type": "string",
                        "description": "ID do agente a ser executado",
                        "required": True
                    },
                    "input_text": {
                        "type": "string",
                        "description": "Texto de entrada para o agente",
                        "required": True
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Temperatura para geração de texto (controla criatividade)",
                        "required": False,
                        "default": 0.7
                    },
                    "model": {
                        "type": "string",
                        "description": "Modelo LLM a ser usado",
                        "required": False
                    },
                    "file_ids": {
                        "type": "array",
                        "description": "Lista de IDs de arquivos a serem utilizados",
                        "required": False,
                        "items": {
                            "type": "string"
                        }
                    },
                    "wait_execution": {
                        "type": "boolean",
                        "description": "Se deve aguardar a conclusão da execução",
                        "required": False,
                        "default": True
                    }
                }
            },
            {
                "name": "tess.upload_file",
                "description": "Faz upload de um arquivo para a plataforma TESS",
                "parameters": {
                    "file_path": {
                        "type": "string",
                        "description": "Caminho do arquivo a ser enviado",
                        "required": True
                    },
                    "process": {
                        "type": "boolean",
                        "description": "Se o arquivo deve ser processado após o upload",
                        "required": False,
                        "default": True
                    }
                }
            },
            {
                "name": "tess.deep_analysis",
                "description": "Realiza uma análise profunda de um texto utilizando agentes especializados",
                "parameters": {
                    "text": {
                        "type": "string",
                        "description": "Texto para análise profunda",
                        "required": True
                    },
                    "focus": {
                        "type": "string",
                        "description": "Foco específico da análise (opcional)",
                        "required": False
                    }
                }
            }
        ]
    
    def _create_agents(self) -> Dict[str, Agent]:
        """
        Cria os agentes do CrewAI para processamento de consultas
        """
        analyst = Agent(
            role="Analista de Consultas",
            goal="Analisar a consulta do usuário para determinar a ferramenta TESS mais adequada",
            backstory="Um especialista em análise de linguagem natural que pode identificar a intenção do usuário.",
            verbose=False,
            allow_delegation=False
        )
        
        executor = Agent(
            role="Executor de Ferramentas",
            goal="Executar a ferramenta TESS correta com os parâmetros adequados",
            backstory="Um especialista em API TESS que sabe como utilizar as ferramentas disponíveis da maneira mais eficiente.",
            verbose=False,
            allow_delegation=False
        )
        
        responder = Agent(
            role="Formatador de Respostas",
            goal="Formatar os resultados de maneira clara e compreensível para o usuário",
            backstory="Um especialista em comunicação que transforma resultados técnicos em respostas amigáveis.",
            verbose=False,
            allow_delegation=False
        )
        
        return {
            "analyst": analyst,
            "executor": executor,
            "responder": responder
        }
    
    def _create_tasks(self, agents, query: str) -> List[Task]:
        """
        Cria as tarefas do CrewAI para processamento de consultas
        """
        # Listar ferramentas disponíveis para contexto
        tools_context = ""
        for tool in self.tess_tools:
            tools_context += f"- {tool['name']}: {tool['description']}\n"
            tools_context += "  Parâmetros:\n"
            
            for param_name, param_info in tool['parameters'].items():
                required = "obrigatório" if param_info.get("required", True) else "opcional"
                default = f", padrão: {param_info.get('default')}" if param_info.get("default") is not None else ""
                tools_context += f"    - {param_name}: {param_info.get('description', '')} ({required}{default})\n"
        
        analyze_task = Task(
            description=f"""
            Analise a seguinte consulta do usuário e determine qual ferramenta TESS deve ser utilizada:
            
            CONSULTA: {query}
            
            FERRAMENTAS DISPONÍVEIS:
            {tools_context}
            
            Sua resposta deve incluir:
            1. A ferramenta TESS mais adequada para a consulta
            2. Os parâmetros que devem ser extraídos da consulta
            3. Justificativa para a escolha
            """,
            agent=agents["analyst"]
        )
        
        execute_task = Task(
            description="""
            Com base na análise anterior, execute a ferramenta TESS recomendada com os parâmetros adequados.
            Se a execução não for possível, forneça uma explicação clara sobre o motivo.
            """,
            agent=agents["executor"],
            context=[analyze_task]
        )
        
        response_task = Task(
            description="""
            Formate o resultado da execução da ferramenta em uma resposta clara e compreensível para o usuário.
            A resposta deve ser direta, evitar jargões técnicos desnecessários e incluir todas as informações relevantes.
            """,
            agent=agents["responder"],
            context=["{{analyze_task.output}}", "{{execute_task.output}}"]
        )
        
        return [analyze_task, execute_task, response_task]
    
    def process_query(self, query: str) -> str:
        """
        Processa uma consulta do usuário e determina qual ferramenta TESS utilizar.
        
        Args:
            query: Consulta do usuário.
            
        Returns:
            String com o resultado do processamento.
        """
        # Verificar se é uma consulta de análise profunda
        if "análise profunda" in query.lower():
            # Extrair o texto a ser analisado
            text_match = re.search(r"análise profunda[^:]*:(.*)", query, re.IGNORECASE | re.DOTALL)
            if text_match:
                text = text_match.group(1).strip()
                return self.deep_analysis(text)
        
        # Se não for uma consulta específica, usar o LLM diretamente
        messages = [
            {"role": "system", "content": "Você é um assistente útil."},
            {"role": "user", "content": query}
        ]
        return self.chat_provider.chat(messages)
    
    def deep_analysis(self, text: str, focus: Optional[str] = None) -> str:
        """
        Realiza uma análise profunda de um texto utilizando agentes especializados.
        
        Args:
            text: Texto para análise profunda.
            focus: Foco específico da análise (opcional).
            
        Returns:
            String com o resultado da análise.
        """
        try:
            # Criar agentes especializados
            researcher = Agent(
                role='Pesquisador',
                goal='Analisar textos e extrair informações valiosas',
                backstory=dedent("""
                    Você é um pesquisador especializado em análise profunda de textos.
                    Sua experiência permite identificar contextos, intenções e extrair 
                    insights valiosos de qualquer tipo de texto.
                """),
                verbose=True,
                allow_delegation=False
            )
            
            analyst = Agent(
                role='Analista',
                goal='Estruturar análises e identificar padrões',
                backstory=dedent("""
                    Você é um analista com capacidade de estruturar informações
                    em formatos claros e identificar padrões relevantes em textos.
                """),
                verbose=True,
                allow_delegation=False
            )
            
            summarizer = Agent(
                role='Sintetizador',
                goal='Sintetizar informações em resumos concisos',
                backstory=dedent("""
                    Você é especialista em transformar análises complexas em
                    resumos concisos e de alto valor, destacando apenas o mais relevante.
                """),
                verbose=True,
                allow_delegation=False
            )
            
            # Criar tarefas
            research_task = Task(
                description=f"""
                Analise o seguinte texto em profundidade:
                
                {text}
                
                {f"Com foco em: {focus}" if focus else ""}
                
                Identifique o contexto, intenções, informações importantes e quaisquer padrões ou características relevantes.
                """,
                agent=researcher
            )
            
            analysis_task = Task(
                description="""
                Com base na pesquisa inicial, estruture uma análise detalhada que inclua:
                
                1. Contexto geral
                2. Pontos principais
                3. Intenções identificadas
                4. Padrões e características relevantes
                5. Principais insights
                
                Organize as informações em um formato claro e estruturado.
                """,
                agent=analyst,
                context=[research_task]
            )
            
            summary_task = Task(
                description="""
                Com base na análise detalhada, crie um resumo conciso e de alto valor que:
                
                1. Capture a essência do texto
                2. Destaque os insights mais valiosos
                3. Apresente conclusões relevantes
                4. Seja direto e objetivo
                
                O resumo deve ser compreensível por qualquer pessoa, mesmo sem contexto adicional.
                """,
                agent=summarizer,
                context=[analysis_task]
            )
            
            # Criar o crew e processar
            crew = Crew(
                agents=[researcher, analyst, summarizer],
                tasks=[research_task, analysis_task, summary_task],
                process=Process.sequential
            )
            
            # Executa e retorna o resultado
            result = crew.kickoff()
            return result
        
        except Exception as e:
            logger.error(f"Erro na análise profunda: {str(e)}")
            # Simulação de resultado em caso de falha na análise via CrewAI
            # Aqui usamos o provedor de chat como fallback
            messages = [
                {"role": "system", "content": "Você é um assistente especializado em análise de textos."},
                {"role": "user", "content": f"Faça uma análise profunda do seguinte texto{f' com foco em {focus}' if focus else ''}: {text}"}
            ]
            return self.chat_provider.chat(messages)

# Exemplo de uso direto (para teste)
if __name__ == "__main__":
    try:
        crew = TessCrew()
        result = crew.process_query("Liste os agentes disponíveis no TESS")
        print(result)
    except Exception as e:
        print(f"Erro: {str(e)}") 