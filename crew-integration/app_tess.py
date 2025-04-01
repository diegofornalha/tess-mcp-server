import streamlit as st
import requests
import json
import os
import subprocess
from dotenv import load_dotenv
import pandas as pd
import time
from urllib.parse import parse_qs

# Carregar variáveis de ambiente
load_dotenv()
TESS_API_KEY = os.getenv("TESS_API_KEY")
TESS_API_URL = "https://tess.pareto.io/api"

# Configurações da página
st.set_page_config(
    page_title="TESS API Interface",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para comunicação com API TESS
def api_request(endpoint, method="GET", data=None):
    url = f"{TESS_API_URL}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {TESS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        
        # Verificar código de status da resposta
        if response.status_code == 200:
            return response.json()
        else:
            # Tentar extrair mensagem de erro da resposta JSON
            try:
                error_data = response.json()
                error_message = error_data.get('message', f'Erro HTTP {response.status_code}')
                return {"error": True, "status_code": response.status_code, "message": error_message, "details": error_data}
            except:
                # Se não for possível extrair JSON, usar o texto da resposta
                return {"error": True, "status_code": response.status_code, "message": response.text}
    except Exception as e:
        # Capturar exceções de conexão ou outras
        return {"error": True, "message": f"Erro de conexão: {str(e)}"}

# Função para obter parâmetros do agente utilizando o CLI
def get_agent_params_cli(agent_id):
    """Obtém parâmetros do agente usando o CLI e processa a saída"""
    try:
        # Executar o comando CLI
        result = subprocess.run(
            ["python", "scripts/tess_api_cli.py", "info", str(agent_id)],
            capture_output=True, 
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode != 0:
            return {"error": True, "message": f"Erro ao executar CLI: {result.stderr}"}
        
        # Processar saída
        output = result.stdout
        
        # Extrair informações
        nome = "N/A"
        descricao = "Sem descrição"
        categoria = "N/A"
        
        # Extrair nome, descrição e categoria
        if "Nome:" in output:
            nome_linha = [line for line in output.split('\n') if "Nome:" in line][0]
            nome = nome_linha.split("Nome:")[1].strip()
        
        if "Descrição:" in output:
            desc_linha = [line for line in output.split('\n') if "Descrição:" in line][0]
            descricao = desc_linha.split("Descrição:")[1].strip()
        
        if "Categoria:" in output:
            cat_linha = [line for line in output.split('\n') if "Categoria:" in line][0]
            categoria = cat_linha.split("Categoria:")[1].strip()
        
        # Extrair parâmetros
        params_secao = output.split("Parâmetros necessários:")[1] if "Parâmetros necessários:" in output else ""
        param_lines = [line.strip() for line in params_secao.split('\n') if line.strip().startswith('- ')]
        
        parametros_obrigatorios = []
        parametros_opcionais = []
        
        for line in param_lines:
            # Remover o traço inicial
            line = line[2:].strip()
            
            # Separar nome e descrição
            if ":" in line:
                param_name, param_desc = line.split(":", 1)
                param_name = param_name.strip()
                param_desc = param_desc.strip()
                
                # Verificar se é obrigatório
                obrigatorio = "* Obrigatório" in param_desc
                
                # Extrair tipo
                param_type = "text"  # padrão
                if "[select]" in param_desc:
                    param_type = "select"
                elif "[number]" in param_desc:
                    param_type = "number"
                elif "[boolean]" in param_desc:
                    param_type = "boolean"
                
                # Limpar descrição
                param_desc = param_desc.replace("[text]", "").replace("[select]", "").replace("[number]", "").replace("[boolean]", "").replace("* Obrigatório", "").strip()
                
                param_info = {
                    "name": param_name,
                    "type": param_type,
                    "description": param_desc
                }
                
                if obrigatorio:
                    parametros_obrigatorios.append(param_info)
                else:
                    parametros_opcionais.append(param_info)
        
        return {
            "obrigatorios": parametros_obrigatorios,
            "opcionais": parametros_opcionais,
            "nome_agente": nome,
            "descricao": descricao,
            "categoria": categoria
        }
    
    except Exception as e:
        print(f"Erro ao obter parâmetros via CLI: {str(e)}")
        # Se falhar com o CLI, usa o método API como fallback
        return get_agent_params(agent_id)

# Função original para obter os parâmetros obrigatórios de um agente via API
def get_agent_params(agent_id):
    """Retorna os parâmetros obrigatórios e opcionais para um agente específico"""
    resultado = api_request(f"agents/{agent_id}")
    
    if "error" in resultado:
        return {"error": resultado.get("message", "Erro ao obter informações do agente")}
    
    parametros_obrigatorios = []
    parametros_opcionais = []
    
    if "questions" in resultado:
        for param in resultado["questions"]:
            param_name = param.get("name", "")
            param_required = param.get("required", False)
            param_type = param.get("type", "text")
            param_description = param.get("description", "")
            
            param_info = {
                "name": param_name,
                "type": param_type,
                "description": param_description
            }
            
            # Adicionar opções se existirem
            if "values" in param or "options" in param:
                options = param.get("values", param.get("options", []))
                param_info["options"] = options
            
            if param_required:
                parametros_obrigatorios.append(param_info)
            else:
                parametros_opcionais.append(param_info)
    
    return {
        "obrigatorios": parametros_obrigatorios,
        "opcionais": parametros_opcionais,
        "nome_agente": resultado.get("name", f"Agente {agent_id}"),
        "descricao": resultado.get("description", "Sem descrição")
    }

# Função para extrair informações do texto usando IA
def extract_info_with_ai(text, agent_id):
    """Usa a API TESS para extrair informações estruturadas a partir de texto livre"""
    prompt = f"""
    Extraia as seguintes informações do texto abaixo:
    - Nome da empresa
    - Descrição do negócio
    - Diferenciais (lista)
    - Call to action

    Se houver outras informações relevantes, como "topico", "objetivo", "seu-instagram", etc., também extraia-as.
    
    Retorne em formato JSON com as chaves: "nome-da-empresa", "descrio", "diferenciais", "call-to-action" e quaisquer outras encontradas.
    
    Texto: {text}
    """
    
    # Analisar com o agente 49 (interpretação de texto)
    analyzer_id = 49  # Usar o agente de escrita criativa ou equivalente
    
    payload = {
        "prompt": prompt,
        "temperature": 0.3,  # Baixa temperatura para respostas mais consistentes
        "model": "gpt-4o",   # Modelo avançado para melhor interpretação
        "waitExecution": True
    }
    
    with st.spinner("Analisando texto..."):
        resultado = api_request(f"agents/{analyzer_id}/execute", method="POST", data=payload)
    
    if "error" in resultado:
        print(f"Erro ao analisar texto com IA: {resultado.get('message', 'Erro desconhecido')}")
        return {}
    
    # Extrair o resultado
    output = ""
    if "responses" in resultado and len(resultado["responses"]) > 0:
        output = resultado["responses"][0].get("output", "")
    elif "response" in resultado:
        output = resultado["response"]
    
    # Tentar extrair JSON do resultado
    try:
        # Procurar por estrutura JSON no texto
        json_start = output.find('{')
        json_end = output.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_text = output[json_start:json_end]
            extracted_data = json.loads(json_text)
            
            # Verificar e formatar as chaves esperadas
            result = {}
            if "nome-da-empresa" in extracted_data:
                result["nome-da-empresa"] = extracted_data["nome-da-empresa"]
            elif "nome" in extracted_data:
                result["nome-da-empresa"] = extracted_data["nome"]
            
            if "descrio" in extracted_data:
                result["descrio"] = extracted_data["descrio"]
            elif "descrição" in extracted_data or "descricao" in extracted_data:
                result["descrio"] = extracted_data.get("descrição", extracted_data.get("descricao", ""))
            
            if "diferenciais" in extracted_data:
                result["diferenciais"] = extracted_data["diferenciais"]
            
            if "call-to-action" in extracted_data:
                result["call-to-action"] = extracted_data["call-to-action"]
            elif "call_to_action" in extracted_data:
                result["call-to-action"] = extracted_data["call_to_action"]
            
            # Incluir outros campos encontrados
            for key, value in extracted_data.items():
                if key not in ["nome-da-empresa", "descrio", "diferenciais", "call-to-action", 
                               "nome", "descrição", "descricao", "call_to_action"]:
                    result[key] = value
            
            return result
    except Exception as e:
        print(f"Erro ao processar resposta JSON: {str(e)}")
    
    return {}

# Interface principal
def main():
    st.title("Gerador de Anúncios com TESS API")
    
    # Sidebar para navegação
    menu = st.sidebar.selectbox(
        "Selecione uma opção",
        ["Gerar Anúncios", "Listar Agentes", "Modelos Disponíveis", "Configurações"],
        index=0  # Garantir que "Gerar Anúncios" seja a opção padrão
    )
    
    if menu == "Listar Agentes":
        listar_agentes_page()
    elif menu == "Gerar Anúncios":
        gerar_anuncios_page()
    elif menu == "Modelos Disponíveis":
        modelos_page()
    elif menu == "Configurações":
        configuracoes_page()

# Página para listar agentes
def listar_agentes_page():
    st.header("Agentes TESS Disponíveis")
    
    # Botão para atualizar a lista
    if st.button("Atualizar Lista de Agentes"):
        with st.spinner("Carregando agentes..."):
            resultado = api_request("agents")
            
            if "data" in resultado:
                # Criar DataFrame para melhor visualização
                agentes = []
                for agente in resultado["data"]:
                    agentes.append({
                        "ID": agente.get("id"),
                        "Nome": agente.get("name", "Nome não disponível"),
                        "Descrição": agente.get("description", "Sem descrição"),
                        "Categoria": agente.get("category", "N/A"),
                    })
                
                # Salvar na session state para uso em outras páginas
                st.session_state["agentes"] = agentes
                
                # Exibir DataFrame
                df = pd.DataFrame(agentes)
                st.dataframe(df)
            else:
                st.error("Não foi possível obter a lista de agentes.")

# Página para gerar anúncios
def gerar_anuncios_page():
    st.header("Gerar Anúncios")
    
    # Verificar se temos um agent_id na URL
    query_params = st.experimental_get_query_params()
    agent_id_param = query_params.get("agent_id", [None])[0]
    
    # Se temos um agent_id na URL e ainda não definimos um agente
    if agent_id_param and not st.session_state.get("agente_selecionado"):
        # Carregar agentes se necessário
        if not st.session_state["agentes"]:
            with st.spinner("Carregando agentes..."):
                result = api_request("agents")
                if "error" not in result:
                    if "data" in result:
                        agents_data = result["data"]
                    else:
                        agents_data = result
                        
                    agentes = []
                    for agent in agents_data:
                        try:
                            agent_id = agent.get("id", "")
                            agent_name = agent.get("name", agent.get("Nome", ""))
                            agent_desc = agent.get("description", agent.get("Descrição", ""))
                            agent_category = agent.get("category", agent.get("Categoria", ""))
                            
                            agentes.append({
                                "ID": agent_id,
                                "Nome": agent_name,
                                "Descrição": agent_desc,
                                "Categoria": agent_category
                            })
                        except Exception as e:
                            continue
                    
                    st.session_state["agentes"] = agentes
        
        # Definir o agente selecionado com base no parâmetro da URL
        st.session_state["agente_selecionado"] = agent_id_param
    
    # Carregar agentes se necessário
    if not st.session_state["agentes"]:
        with st.spinner("Carregando agentes..."):
            result = api_request("agents")
            if "error" in result:
                st.error(f"Erro ao carregar agentes: {result['error']}")
                return
                
            if "data" in result:
                agents_data = result["data"]
            else:
                agents_data = result
                
            agentes = []
            for agent in agents_data:
                try:
                    agent_id = agent.get("id", "")
                    agent_name = agent.get("name", agent.get("Nome", ""))
                    agent_desc = agent.get("description", agent.get("Descrição", ""))
                    agent_category = agent.get("category", agent.get("Categoria", ""))
                    
                    agentes.append({
                        "ID": agent_id,
                        "Nome": agent_name,
                        "Descrição": agent_desc,
                        "Categoria": agent_category
                    })
                except Exception as e:
                    st.warning(f"Erro ao processar agente: {str(e)}")
                    continue
            
            st.session_state["agentes"] = agentes
    
    # Criar seletor de agentes
    agent_options = {f"{a['ID']} - {a['Descrição']}": a['ID'] for a in st.session_state["agentes"]}
    
    # Usar o agente da URL ou o último selecionado
    default_label = None
    if st.session_state.get("agente_selecionado"):
        # Encontrar a chave correspondente ao valor
        for key, value in agent_options.items():
            if value == st.session_state["agente_selecionado"]:
                default_label = key
                break
    
    selected_agent_label = st.selectbox(
        "Selecione um agente:",
        options=list(agent_options.keys()),
        index=list(agent_options.keys()).index(default_label) if default_label else 0
    )
    
    selected_agent_id = agent_options[selected_agent_label]
    st.session_state["agente_selecionado"] = selected_agent_id
    
    # Verificar se o agente existe e obter seus parâmetros
    with st.spinner("Carregando detalhes do agente..."):
        result = api_request(f"agents/{selected_agent_id}")
        if "error" in result:
            st.error(f"Erro ao carregar detalhes do agente: {result['error']}")
            return
        
        agent_detail = result
        
        # Verificar o formato da resposta
        if "questions" in agent_detail:
            agent_params = agent_detail["questions"]
        elif "data" in agent_detail and "questions" in agent_detail["data"]:
            agent_params = agent_detail["data"]["questions"]
        else:
            st.error("Formato de resposta inesperado. Não foi possível encontrar os parâmetros do agente.")
            return
    
    # Criar formulário para parâmetros do agente
    with st.form("params_form"):
        st.subheader("Parâmetros do Agente")
        
        params_values = {}
        
        # Para cada parâmetro, criar campo apropriado
        for param in agent_params:
            param_id = param.get("id")
            param_name = param.get("name", param_id)
            param_type = param.get("type", "text")
            param_description = param.get("description", "")
            param_required = param.get("required", False)
            
            # Diferentes tipos de inputs com base no tipo de parâmetro
            if param_type == "select" and "options" in param:
                options = param["options"] if isinstance(param["options"], list) else param.get("values", [])
                option_values = [opt.get("value", opt) if isinstance(opt, dict) else opt for opt in options]
                option_labels = [opt.get("label", opt.get("value", opt)) if isinstance(opt, dict) else opt for opt in options]
                
                option_dict = {label: value for label, value in zip(option_labels, option_values)}
                
                selected_option = st.selectbox(
                    f"{param_name}{' *' if param_required else ''}",
                    options=option_labels,
                    help=param_description
                )
                
                params_values[param_id] = option_dict[selected_option]
                
            elif param_type == "number":
                params_values[param_id] = st.number_input(
                    f"{param_name}{' *' if param_required else ''}",
                    min_value=param.get("min", 0.0),
                    max_value=param.get("max", 100.0),
                    value=param.get("default", 1.0),
                    step=0.01,
                    help=param_description
                )
                
            elif param_type == "textarea":
                params_values[param_id] = st.text_area(
                    f"{param_name}{' *' if param_required else ''}",
                    value=param.get("default", ""),
                    height=150,
                    help=param_description
                )
                
            else:  # text é o padrão
                params_values[param_id] = st.text_input(
                    f"{param_name}{' *' if param_required else ''}",
                    value=param.get("default", ""),
                    help=param_description
                )
        
        # Opções de saída
        st.subheader("Opções de Saída")
        output_format = st.selectbox(
            "Formato de Saída",
            options=["Markdown", "JSON", "Texto puro"],
            index=0
        )
        st.session_state["formato_saida"] = output_format
        
        # Botão de envio
        submit_button = st.form_submit_button("Gerar")
    
    # Processar envio
    if submit_button:
        # Verificar campos obrigatórios
        missing_fields = []
        for param in agent_params:
            if param.get("required", False) and not params_values.get(param["id"]):
                missing_fields.append(param.get("name", param["id"]))
        
        if missing_fields:
            st.error(f"Campos obrigatórios não preenchidos: {', '.join(missing_fields)}")
            return
        
        # Enviar requisição para a API
        with st.spinner("Gerando conteúdo..."):
            payload = {
                "agent_id": selected_agent_id,
                "parameters": params_values
            }
            
            result = api_request("run_agent", method="POST", data=payload)
            
            if "error" in result:
                st.error(f"Erro ao gerar conteúdo: {result['error']}")
                if "message" in result:
                    st.error(f"Detalhes: {result['message']}")
                return
            
            # Exibir resultados
            st.success("Conteúdo gerado com sucesso!")
            
            # Processar resposta conforme o formato
            if "answer" in result:
                content = result["answer"]
            elif "data" in result and "answer" in result["data"]:
                content = result["data"]["answer"]
            else:
                content = json.dumps(result, indent=2)
            
            # Exibir conforme formato selecionado
            if output_format == "Markdown":
                st.markdown(content)
            elif output_format == "JSON":
                st.json(json.loads(content) if isinstance(content, str) else content)
            else:  # Texto puro
                st.text(content)
            
            # Botão para download dos resultados
            timestamp = int(time.time())
            if output_format == "Markdown":
                filename = f"resultado_{selected_agent_id}_{timestamp}.md"
                st.download_button(
                    label="Download dos Resultados (Markdown)",
                    data=content,
                    file_name=filename,
                    mime="text/markdown"
                )
            elif output_format == "JSON":
                filename = f"resultado_{selected_agent_id}_{timestamp}.json"
                st.download_button(
                    label="Download dos Resultados (JSON)",
                    data=content if isinstance(content, str) else json.dumps(content, indent=2),
                    file_name=filename,
                    mime="application/json"
                )
            else:  # Texto puro
                filename = f"resultado_{selected_agent_id}_{timestamp}.txt"
                st.download_button(
                    label="Download dos Resultados (Texto)",
                    data=content,
                    file_name=filename,
                    mime="text/plain"
                )

# Página para listar modelos disponíveis
def modelos_page():
    st.header("Modelos Disponíveis")
    
    # Parâmetro opcional: ID do agente para consultar
    agent_id = st.number_input("ID do Agente:", min_value=1, value=45)
    
    if st.button("Listar Modelos"):
        with st.spinner("Carregando modelos..."):
            resultado = api_request(f"agents/{agent_id}")
            
            if "error" not in resultado:
                # Recomendados primeiro
                st.subheader("Modelos Recomendados")
                recomendados = [
                    {"nome": "GPT-4o", "valor": "gpt-4o", "desc": "Versão avançada do GPT-4 com recursos multimodais - Recomendado"},
                    {"nome": "Claude 3.5 Sonnet", "valor": "claude-3-5-sonnet-20240620", "desc": "Bom balanceamento entre velocidade e qualidade"},
                    {"nome": "GPT-4o mini", "valor": "gpt-4o-mini", "desc": "Versão mais rápida e econômica do GPT-4o"}
                ]
                
                for modelo in recomendados:
                    st.markdown(f"⭐ **{modelo['nome']}** (`{modelo['valor']}`)")
                    st.markdown(f"  {modelo['desc']}")
                
                # Procurar modelos do agente
                if "questions" in resultado:
                    model_param = None
                    for param in resultado["questions"]:
                        if param.get("name") == "model":
                            model_param = param
                            break
                    
                    if model_param and ("values" in model_param or "options" in model_param):
                        options = model_param.get("values", model_param.get("options", []))
                        
                        st.subheader("Todos os Modelos Disponíveis")
                        
                        # DataFrame para visualização
                        modelos_list = []
                        for option in options:
                            if isinstance(option, str):
                                modelos_list.append({"Modelo": option})
                            elif isinstance(option, dict):
                                modelos_list.append({
                                    "Modelo": option.get("label", option.get("value", "N/A")),
                                    "Valor": option.get("value", "N/A")
                                })
                        
                        st.dataframe(pd.DataFrame(modelos_list))
                    else:
                        st.warning("Estrutura de modelos não encontrada no formato esperado.")
                else:
                    st.warning("Nenhuma informação de parâmetros encontrada para este agente.")
            else:
                st.error(f"Erro ao obter informações: {resultado.get('message', 'Erro desconhecido')}")

# Página de configurações
def configuracoes_page():
    st.header("Configurações")
    
    # API Key
    current_key = os.getenv("TESS_API_KEY")
    masked_key = current_key[:4] + "*" * (len(current_key) - 8) + current_key[-4:] if current_key else ""
    
    st.subheader("API TESS")
    api_key = st.text_input("Chave da API TESS:", value=masked_key, type="password")
    
    # Opções de formato de saída
    st.subheader("Formato de Saída")
    formato = st.radio("Formato de saída padrão:", ["Formatado", "JSON", "Texto puro"])
    
    # Salvar configurações
    if st.button("Salvar Configurações"):
        # Aqui você implementaria a lógica para salvar as configurações
        # Isso pode envolver a atualização do arquivo .env ou uso de st.session_state
        st.success("Configurações salvas com sucesso!")

if __name__ == "__main__":
    main() 