import streamlit as st
import requests
import json
import time
import pandas as pd

st.set_page_config(
    page_title="TESS-MCP Interface",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4A8CFF;
    }
    .tool-header {
        color: #4A8CFF;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .success-text {
        color: #4CAF50;
    }
    .error-text {
        color: #F44336;
    }
    .info-box {
        background-color: #F0F2F6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 10px;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Configurações
TESS_MCP_URL = "http://localhost:3001"

# Funções para interagir com o servidor MCP-TESS
def list_tools():
    try:
        response = requests.post(f"{TESS_MCP_URL}/tools/list")
        return response.json()['tools']
    except Exception as e:
        st.error(f"Erro ao listar ferramentas: {str(e)}")
        return []

def call_tool(name, arguments):
    try:
        response = requests.post(
            f"{TESS_MCP_URL}/tools/call",
            json={"name": name, "arguments": arguments}
        )
        return response.json()
    except Exception as e:
        st.error(f"Erro ao chamar ferramenta: {str(e)}")
        return {"error": str(e), "isError": True}

def check_server_status():
    try:
        response = requests.get(f"{TESS_MCP_URL}/health")
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Auxiliar para tratar argumentos
def process_arguments(form_values, parameters):
    result = {}
    for param in parameters:
        param_name = param['name']
        param_type = param.get('type', 'string')
        
        if param_name in form_values:
            value = form_values[param_name]
            
            # Tratar valor vazio
            if value == "" and not param.get('required', False):
                continue
                
            # Converter tipos
            if param_type == 'number' and isinstance(value, str):
                try:
                    result[param_name] = float(value)
                except:
                    result[param_name] = value
            elif param_type == 'boolean' and isinstance(value, str):
                result[param_name] = value.lower() in ['true', 'yes', '1', 't', 'y']
            elif param_type == 'array' and isinstance(value, str):
                result[param_name] = [item.strip() for item in value.split(",")] if value else []
            else:
                result[param_name] = value
                
    return result

# Interface principal
st.markdown("<h1 class='main-header'>TESS-MCP Interface</h1>", unsafe_allow_html=True)
st.markdown("Esta interface conecta-se diretamente ao servidor TESS-MCP e utiliza apenas ferramentas TESS. Para interação com modelos de linguagem como Arcee ou OpenAI, utilize a interface CrewAI.")

# Verificar estado do servidor
server_status = check_server_status()
if server_status.get("status") == "ok":
    st.success(f"✅ Servidor conectado: {server_status.get('message', 'Operacional')}")
    if "version" in server_status:
        st.caption(f"Versão: {server_status['version']}")
else:
    st.error(f"❌ Servidor desconectado: {server_status.get('message', 'Erro desconhecido')}")
    st.warning("Verifique se o servidor TESS-MCP está rodando na porta 3001")
    st.stop()

# Abas principais
tab1, tab2, tab3 = st.tabs(["📋 Executar Ferramentas", "📊 Explorar Agentes", "📖 Histórico"])

with tab1:
    # Sidebar para seleção de ferramenta
    st.sidebar.title("Ferramentas TESS")
    st.sidebar.info("Selecione uma ferramenta para executar")

    # Botão para atualizar a lista de ferramentas
    if st.sidebar.button("Atualizar Lista de Ferramentas"):
        st.session_state.tools = list_tools()
        st.sidebar.success("✅ Lista atualizada!")

    # Inicializa a lista de ferramentas se não existir
    if 'tools' not in st.session_state:
        st.session_state.tools = list_tools()

    # Cria a seleção de ferramentas na sidebar
    tool_names = [tool['name'] for tool in st.session_state.tools]
    selected_tool = st.sidebar.selectbox("Selecione uma ferramenta", tool_names)

    # Mostra informações da ferramenta selecionada
    if selected_tool:
        tool = next((t for t in st.session_state.tools if t['name'] == selected_tool), None)
        
        if tool:
            st.markdown(f"<h2 class='tool-header'>{tool['name']}</h2>", unsafe_allow_html=True)
            st.markdown(f"**Descrição:** {tool['description']}")
            
            st.subheader("Parâmetros")
            
            # Criar formulário para os parâmetros da ferramenta
            with st.form(key=f"tool_form_{selected_tool}"):
                form_values = {}
                
                for param in tool['parameters']:
                    param_name = param['name']
                    param_desc = param.get('description', '')
                    param_required = param.get('required', False)
                    param_default = param.get('default', None)
                    param_type = param.get('type', 'string')
                    
                    label = f"{param_name}{' *' if param_required else ''}"
                    help_text = f"{param_desc}"
                    
                    if param_type == 'string':
                        form_values[param_name] = st.text_input(
                            label, 
                            value=param_default or "", 
                            help=help_text
                        )
                    elif param_type == 'number':
                        form_values[param_name] = st.number_input(
                            label, 
                            value=float(param_default or 0), 
                            help=help_text,
                            step=1.0
                        )
                    elif param_type == 'boolean':
                        form_values[param_name] = st.checkbox(
                            label, 
                            value=bool(param_default), 
                            help=help_text
                        )
                    elif param_type == 'array':
                        arr_input = st.text_input(
                            label, 
                            value=",".join(param_default or []), 
                            help=f"{help_text} (separe por vírgulas)"
                        )
                        form_values[param_name] = arr_input
                
                submit_button = st.form_submit_button("Executar")
            
            if submit_button:
                st.info("Executando ferramenta... aguarde.")
                
                # Processar argumentos
                args = process_arguments(form_values, tool['parameters'])
                
                # Mostrar spinner enquanto executa
                with st.spinner(f"Executando {tool['name']}..."):
                    result = call_tool(tool['name'], args)
                
                # Exibir resultado com formatação adequada
                st.subheader("Resultado")
                
                if result.get('isError'):
                    st.markdown("<div class='error-text'>❌ Erro na execução</div>", unsafe_allow_html=True)
                    st.json(result)
                else:
                    st.markdown("<div class='success-text'>✅ Execução bem-sucedida</div>", unsafe_allow_html=True)
                    
                    # Tratar o conteúdo de texto
                    if 'content' in result and isinstance(result['content'], list):
                        for item in result['content']:
                            if item.get('type') == 'text' and item.get('text'):
                                try:
                                    # Tentar analisar como JSON
                                    json_data = json.loads(item['text'])
                                    
                                    # Se tiver dados em formato de lista, mostrar como tabela
                                    if isinstance(json_data, dict) and 'data' in json_data and isinstance(json_data['data'], list):
                                        df = pd.DataFrame(json_data['data'])
                                        st.dataframe(df)
                                    else:
                                        # Mostrar JSON formatado
                                        st.json(json_data)
                                except:
                                    # Se não for JSON, mostrar como texto
                                    st.markdown(f"<div class='info-box'>{item['text']}</div>", unsafe_allow_html=True)
                    else:
                        st.json(result)
                
                # Salvar o resultado na história
                if 'history' not in st.session_state:
                    st.session_state.history = []
                
                st.session_state.history.append({
                    'tool': tool['name'],
                    'params': args,
                    'result': result,
                    'time': time.strftime('%Y-%m-%d %H:%M:%S')
                })

with tab2:
    st.header("Explorador de Agentes TESS")
    
    # Botões para carregar agentes
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Carregar Agentes"):
            st.session_state.tess_agents = call_tool("tess.list_agents", {"page": 1, "per_page": 20})
    with col2:
        agent_query = st.text_input("Pesquisar agentes", placeholder="Digite para filtrar...")
    
    # Mostrar agentes
    if 'tess_agents' in st.session_state and st.session_state.tess_agents:
        try:
            # Extrair e processar os agentes
            content = st.session_state.tess_agents.get('content', [])
            if content and len(content) > 0 and 'text' in content[0]:
                agents_data = json.loads(content[0]['text'])
                
                if isinstance(agents_data, dict) and 'data' in agents_data:
                    agents = agents_data['data']
                    
                    # Filtrar por pesquisa se necessário
                    if agent_query:
                        filtered_agents = [a for a in agents if agent_query.lower() in a.get('title', '').lower() 
                                          or agent_query.lower() in a.get('description', '').lower()]
                    else:
                        filtered_agents = agents
                    
                    # Exibir como cards
                    for i in range(0, len(filtered_agents), 3):
                        cols = st.columns(3)
                        for j in range(3):
                            if i+j < len(filtered_agents):
                                agent = filtered_agents[i+j]
                                with cols[j]:
                                    with st.container(border=True):
                                        st.markdown(f"<h3>{agent.get('title', 'Sem título')}</h3>", unsafe_allow_html=True)
                                        st.caption(f"ID: {agent.get('id', 'N/A')}")
                                        st.markdown(agent.get('description', 'Sem descrição'))
                                        st.markdown(f"Tipo: {agent.get('type', 'N/A')}")
                                        
                                        # Botões de ação
                                        col_a, col_b = st.columns(2)
                                        with col_a:
                                            if st.button(f"Detalhes #{agent.get('id')}", key=f"detail_{agent.get('id')}"):
                                                st.session_state.selected_agent = call_tool("tess.get_agent", {"agent_id": str(agent.get('id'))})
                                        with col_b:
                                            if st.button(f"Executar #{agent.get('id')}", key=f"exec_{agent.get('id')}"):
                                                st.session_state.current_agent_id = agent.get('id')
                                                st.session_state.show_execution_form = True
        except Exception as e:
            st.error(f"Erro ao processar agentes: {str(e)}")
    
    # Mostrar detalhes do agente selecionado
    if 'selected_agent' in st.session_state and st.session_state.selected_agent:
        st.divider()
        st.subheader("Detalhes do Agente")
        
        try:
            content = st.session_state.selected_agent.get('content', [])
            if content and len(content) > 0 and 'text' in content[0]:
                agent_details = json.loads(content[0]['text'])
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"## {agent_details.get('title', 'Sem título')}")
                    st.markdown(f"**Descrição:** {agent_details.get('long_description', agent_details.get('description', 'Sem descrição'))}")
                    st.markdown(f"**Tipo:** {agent_details.get('type', 'N/A')}")
                    st.markdown(f"**Criado em:** {agent_details.get('created_at', 'N/A')}")
                    st.markdown(f"**Atualizado em:** {agent_details.get('updated_at', 'N/A')}")
                
                with col2:
                    st.markdown("### Ações")
                    if st.button("Executar este Agente"):
                        st.session_state.current_agent_id = agent_details.get('id')
                        st.session_state.show_execution_form = True
                
                st.markdown("### Parâmetros")
                if 'questions' in agent_details:
                    for question in agent_details['questions']:
                        with st.expander(f"{question.get('name')}: {question.get('description', '')}"):
                            st.markdown(f"**Tipo:** {question.get('type', 'N/A')}")
                            st.markdown(f"**Obrigatório:** {'Sim' if question.get('required', False) else 'Não'}")
                            if 'options' in question:
                                st.markdown("**Opções:**")
                                for option in question['options']:
                                    st.markdown(f"- {option}")
        except Exception as e:
            st.error(f"Erro ao processar detalhes do agente: {str(e)}")
    
    # Formulário de execução de agente
    if 'show_execution_form' in st.session_state and st.session_state.show_execution_form:
        st.divider()
        st.subheader("Executar Agente")
        
        with st.form(key="execute_agent_form"):
            agent_id = st.session_state.current_agent_id
            input_text = st.text_area("Texto de entrada", height=150)
            
            col1, col2 = st.columns(2)
            with col1:
                model = st.selectbox("Modelo", ["tess-ai-light", "tess-ai-3", "gpt-4o", "claude-3-5-sonnet-latest"])
            with col2:
                temperature = st.slider("Temperatura", 0.0, 1.0, 0.7, 0.1)
            
            wait_execution = st.checkbox("Aguardar conclusão da execução", value=True)
            
            if st.form_submit_button("Executar"):
                args = {
                    "agent_id": str(agent_id),
                    "input_text": input_text,
                    "model": model,
                    "temperature": str(temperature),
                    "wait_execution": wait_execution
                }
                
                with st.spinner("Executando agente..."):
                    result = call_tool("tess.execute_agent", args)
                
                st.session_state.agent_result = result
                
                # Salvar o resultado na história
                if 'history' not in st.session_state:
                    st.session_state.history = []
                
                st.session_state.history.append({
                    'tool': "tess.execute_agent",
                    'params': args,
                    'result': result,
                    'time': time.strftime('%Y-%m-%d %H:%M:%S')
                })
    
    # Mostrar resultado da execução do agente
    if 'agent_result' in st.session_state:
        st.divider()
        st.subheader("Resultado da Execução")
        
        result = st.session_state.agent_result
        
        if result.get('isError'):
            st.error("❌ Erro na execução")
            st.json(result)
        else:
            st.success("✅ Execução bem-sucedida")
            
            # Tratar o conteúdo de texto
            if 'content' in result and isinstance(result['content'], list):
                for item in result['content']:
                    if item.get('type') == 'text' and item.get('text'):
                        try:
                            # Tentar analisar como JSON
                            json_data = json.loads(item['text'])
                            st.json(json_data)
                        except:
                            # Se não for JSON, mostrar como texto
                            st.markdown(item['text'])
            else:
                st.json(result)

with tab3:
    st.header("Histórico de Execuções")
    
    if 'history' in st.session_state and st.session_state.history:
        if st.button("Limpar Histórico"):
            st.session_state.history = []
            st.experimental_rerun()
        
        for i, entry in enumerate(reversed(st.session_state.history)):
            with st.expander(f"{entry['time']} - {entry['tool']}"):
                st.subheader("Parâmetros")
                st.json(entry['params'])
                
                st.subheader("Resultado")
                result = entry['result']
                
                if result.get('isError'):
                    st.error("❌ Erro na execução")
                    st.json(result)
                else:
                    st.success("✅ Execução bem-sucedida")
                    
                    # Tratar o conteúdo de texto
                    if 'content' in result and isinstance(result['content'], list):
                        for item in result['content']:
                            if item.get('type') == 'text' and item.get('text'):
                                try:
                                    # Tentar analisar como JSON
                                    json_data = json.loads(item['text'])
                                    st.json(json_data)
                                except:
                                    # Se não for JSON, mostrar como texto
                                    st.markdown(item['text'])
                    else:
                        st.json(result)
    else:
        st.info("Nenhuma execução registrada ainda.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    "Esta interface se conecta ao servidor TESS-MCP "
    "rodando na porta 3001. Certifique-se de que o servidor "
    "esteja em execução antes de usar esta interface."
)
st.sidebar.caption("Versão 1.0.0") 