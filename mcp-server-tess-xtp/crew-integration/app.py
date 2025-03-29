import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import os
import re
import time
from typing import Dict, List, Any
from dotenv import load_dotenv

from tess_crew import TessCrew

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração da página do Streamlit
st.set_page_config(
    page_title="MCP-TESS com CrewAI",
    page_icon="🤖",
    layout="wide",
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .tool-header {
        background-color: #1E1E1E;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        cursor: pointer;
    }
    .tool-content {
        background-color: #262730;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .code-block {
        background-color: #0E1117;
        padding: 10px;
        border-radius: 5px;
        font-family: monospace;
        white-space: pre-wrap;
    }
    .server-available {
        color: #0BDA51;
        font-weight: bold;
    }
    .server-unavailable {
        color: #FF4B4B;
        font-weight: bold;
    }
    .tool-chip {
        background-color: #4B4DFF;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8em;
        margin-right: 5px;
        display: inline-block;
    }
    .details-container {
        border-left: 3px solid #4B4DFF;
        padding-left: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Função para verificar a saúde do servidor MCP-TESS
def check_server_health(server_url: str) -> bool:
    try:
        # Aumentando o timeout e tentando múltiplas vezes para melhorar a confiabilidade
        for _ in range(3):  # Tentar 3 vezes
            try:
                response = requests.get(f"{server_url}/health", timeout=10)
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                time.sleep(1)  # Esperar 1 segundo antes de tentar novamente
                continue
        return False
    except Exception as e:
        st.sidebar.error(f"Erro ao verificar servidor: {str(e)}")
        return False

# Função para obter lista de ferramentas disponíveis
def get_available_tools(crew: TessCrew) -> List[Dict[str, Any]]:
    if not crew:
        return []
    return crew.tess_tools

# Função para renderizar um bloco de código
def render_code_block(code: str, language: str = "python"):
    st.markdown(f'<div class="code-block">{code}</div>', unsafe_allow_html=True)

# Função para renderizar um bloco de ferramenta expansível
def render_tool_block(tool_name: str, tool_content: str):
    tool_id = re.sub(r'\W+', '', tool_name).lower()
    
    if f"expand_{tool_id}" not in st.session_state:
        st.session_state[f"expand_{tool_id}"] = False
    
    # Header clicável
    header_html = f"""
    <div class="tool-header" id="header_{tool_id}" onclick="toggleTool('{tool_id}')">
        <strong>🛠️ {tool_name}</strong>
        <span style="float: right;">{'+' if not st.session_state[f'expand_{tool_id}'] else '-'}</span>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    
    # Conteúdo expansível
    if st.session_state[f"expand_{tool_id}"]:
        st.markdown(f'<div class="tool-content" id="content_{tool_id}">{tool_content}</div>', unsafe_allow_html=True)

    # JavaScript para alternância
    st.markdown("""
    <script>
    function toggleTool(toolId) {
        const contentDiv = document.getElementById('content_' + toolId);
        const headerDiv = document.getElementById('header_' + toolId);
        
        // Usar o Streamlit para atualizar o estado da sessão
        window.parent.postMessage({
            type: "streamlit:setComponentValue",
            value: !headerDiv.querySelector('span').textContent === '+',
            key: "expand_" + toolId
        }, "*");
    }
    </script>
    """, unsafe_allow_html=True)

# Inicializações
if "history" not in st.session_state:
    st.session_state.history = []

if "servers" not in st.session_state:
    # Obter URLs dos servidores a partir do arquivo .env
    local_url = os.getenv("MCP_LOCAL_SERVER_URL", "http://localhost:3001")
    prod_url = os.getenv("MCP_PROD_SERVER_URL", "http://prod-mcp-tess:3001")
    
    st.session_state.servers = [
        {"name": "MCP-TESS Local", "url": local_url},
        {"name": "MCP-TESS Produção", "url": prod_url}
    ]

if "selected_server" not in st.session_state:
    st.session_state.selected_server = st.session_state.servers[0]

# Verificar a disponibilidade de ambos os servidores
if "server_status" not in st.session_state:
    st.session_state.server_status = {}

# Verificar ambos os servidores  
for server in st.session_state.servers:
    st.session_state.server_status[server["url"]] = check_server_health(server["url"])

# Atualizar a disponibilidade do servidor selecionado
st.session_state.server_available = st.session_state.server_status[st.session_state.selected_server["url"]]

# Mostrar informações de debug no início para auxiliar na identificação de problemas
st.sidebar.write(f"Verificando servidor: {st.session_state.selected_server['url']}")

if "crew" not in st.session_state and st.session_state.server_available:
    try:
        # Atualizar a variável de ambiente para o servidor selecionado
        os.environ["MCP_TESS_HOST"] = st.session_state.selected_server["url"]
        st.session_state.crew = TessCrew()
    except Exception as e:
        st.sidebar.error(f"Erro ao inicializar o CrewAI: {str(e)}")
        st.session_state.server_available = False

# Barra lateral
with st.sidebar:
    st.title("MCP-TESS com CrewAI")
    
    # Status de todos os servidores
    st.subheader("Status dos Servidores")
    for server in st.session_state.servers:
        status = st.session_state.server_status[server["url"]]
        if status:
            st.markdown(f'<p class="server-available">✅ {server["name"]} disponível</p>', unsafe_allow_html=True)
        else:
            st.markdown(f'<p class="server-unavailable">❌ {server["name"]} indisponível</p>', unsafe_allow_html=True)
    
    # Seleção de servidor
    st.subheader("Servidor MCP")
    server_options = [server["name"] for server in st.session_state.servers]
    selected_server_name = st.selectbox("Selecione o servidor:", server_options, index=server_options.index(st.session_state.selected_server["name"]))
    
    # Atualizar servidor selecionado
    if selected_server_name != st.session_state.selected_server["name"]:
        for server in st.session_state.servers:
            if server["name"] == selected_server_name:
                st.session_state.selected_server = server
                st.session_state.server_available = st.session_state.server_status[server["url"]]
                
                if st.session_state.server_available:
                    try:
                        # Atualizar a variável de ambiente para o servidor selecionado
                        os.environ["MCP_TESS_HOST"] = server["url"]
                        st.session_state.crew = TessCrew()
                    except Exception as e:
                        st.error(f"Erro ao inicializar o CrewAI: {str(e)}")
                        st.session_state.server_available = False
                else:
                    if "crew" in st.session_state:
                        del st.session_state.crew
                
                st.rerun()
    
    # Informações específicas para o servidor selecionado se estiver indisponível
    if not st.session_state.server_available:
        server_info = f"""
        <div style="background-color: #262730; padding: 10px; border-radius: 5px; margin-top: 10px;">
        <p>Tentando conectar a: <code>{st.session_state.selected_server['url']}/health</code></p>
        <p>Certifique-se de que o servidor MCP-TESS está em execução usando:</p>
        <code>cd /Users/agents/Desktop/crew_ai_tess_pareto && ./scripts/iniciar_tess_mcp_dev.sh</code>
        </div>
        """
        st.markdown(server_info, unsafe_allow_html=True)
        
        if st.button("Verificar novamente"):
            # Atualizar o status de todos os servidores
            for server in st.session_state.servers:
                st.session_state.server_status[server["url"]] = check_server_health(server["url"])
            
            # Atualizar o status do servidor selecionado
            server_health = st.session_state.server_status[st.session_state.selected_server["url"]]
            st.session_state.server_available = server_health
            
            if server_health and "crew" not in st.session_state:
                try:
                    # Atualizar a variável de ambiente para o servidor selecionado
                    os.environ["MCP_TESS_HOST"] = st.session_state.selected_server["url"]
                    st.session_state.crew = TessCrew()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao inicializar o CrewAI: {str(e)}")
            elif server_health:
                st.rerun()
    
    # Ferramentas disponíveis
    if st.session_state.server_available and "crew" in st.session_state:
        st.divider()
        st.subheader("Ferramentas TESS disponíveis")
        
        tools = get_available_tools(st.session_state.crew)
        for tool in tools:
            with st.expander(f"{tool['name']}"):
                st.write(f"**Descrição:** {tool['description']}")
                st.write("**Parâmetros:**")
                for param_name, param_info in tool['parameters'].items():
                    required = "obrigatório" if param_info.get("required", True) else "opcional"
                    default = f", padrão: {param_info.get('default')}" if param_info.get("default") is not None else ""
                    st.write(f"- **{param_name}** ({required}{default}): {param_info.get('description', '')}")
    
    st.divider()
    st.markdown("### Sobre")
    st.markdown("""
    Esta aplicação conecta o servidor MCP-TESS com o framework CrewAI 
    para orquestrar agentes especializados que auxiliam no processamento 
    de consultas utilizando as ferramentas TESS.
    """)

# Interface principal
st.title("MCP-TESS com CrewAI")

# Se o servidor estiver indisponível, mostrar instruções para iniciar
if not st.session_state.server_available:
    st.warning("O servidor MCP-TESS não está disponível.")
    with st.expander("Como iniciar o servidor MCP-TESS"):
        st.code("""
        # Abra um novo terminal e execute:
        cd /Users/agents/Desktop/crew_ai_tess_pareto
        ./scripts/iniciar_tess_mcp_dev.sh
        
        # Ou, para iniciar em segundo plano:
        ./scripts/iniciar_tess_mcp_prod.sh
        
        # Depois, atualize esta página e clique em "Verificar novamente" na barra lateral
        """)
    
    # Exibir uma mensagem amigável para o usuário
    st.info("Por favor, inicie o servidor MCP-TESS para continuar usando a aplicação.")
    st.stop()  # Parar a execução aqui se o servidor não estiver disponível

# Área de entrada da consulta
with st.form("query_form"):
    query = st.text_area("Digite sua consulta:", height=150)
    submitted = st.form_submit_button("Enviar")

# Processamento da consulta
if submitted:
    if not query:
        st.warning("Por favor, digite uma consulta.")
    elif not st.session_state.server_available:
        st.warning("O servidor MCP-TESS não está disponível. Verifique a conexão e tente novamente.")
    else:
        with st.spinner("Processando sua consulta..."):
            try:
                # Processar a consulta usando o CrewAI
                result = st.session_state.crew.process_query(query)
                
                # Adicionar ao histórico
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Extrair as ferramentas usadas (simulação)
                tools_used = []
                for tool in st.session_state.crew.tess_tools:
                    # Verificar se o nome da ferramenta aparece no resultado
                    if tool['name'] in result:
                        tools_used.append({
                            "name": tool['name'],
                            "description": tool['description'],
                            "result": f"Exemplo de resultado para {tool['name']}"
                        })
                
                st.session_state.history.append({
                    "timestamp": timestamp,
                    "query": query,
                    "result": result,
                    "tools_used": tools_used
                })
                
                # Exibir resultado
                st.success("Consulta processada com sucesso!")
                
                # Exibir as ferramentas usadas num formato expansível
                if tools_used:
                    st.markdown("### Ferramentas Utilizadas:")
                    for tool in tools_used:
                        with st.expander(f"🛠️ {tool['name']}"):
                            st.markdown(f"**Descrição:** {tool['description']}")
                            st.markdown(f"**Resultado:**")
                            st.code(tool['result'], language="json")
                
                # Exibir o resultado final
                st.markdown("### Resultado Final:")
                st.markdown(result)
            
            except Exception as e:
                st.error(f"Erro ao processar a consulta: {str(e)}")

# Exibir histórico
if st.session_state.history:
    st.divider()
    st.markdown("### Histórico de Consultas")
    
    for i, item in enumerate(reversed(st.session_state.history)):
        with st.expander(f"{item['timestamp']} - {item['query'][:50]}{'...' if len(item['query']) > 50 else ''}"):
            st.markdown(f"**Consulta completa:**")
            st.markdown(item['query'])
            
            if "tools_used" in item and item["tools_used"]:
                st.markdown("**Ferramentas utilizadas:**")
                for tool in item["tools_used"]:
                    st.markdown(f"- {tool['name']}")
            
            st.markdown("**Resultado:**")
            st.markdown(item["result"])

# Rodapé
st.markdown("---")
st.markdown(
    "**TESS-MCP com CrewAI** | Desenvolvido com ❤️ para facilitar o acesso às ferramentas TESS",
    help="Integração das ferramentas TESS via MCP utilizando agentes CrewAI"
) 