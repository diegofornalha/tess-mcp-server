import streamlit as st
import requests
import json
import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
import base64
import time
import re

# Carregando as variáveis de ambiente
load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="Filtro de Agentes TESS",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuração visual
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .agent-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 10px;
        transition: transform 0.3s;
    }
    .agent-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    .card-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .card-id {
        font-size: 14px;
        color: #666;
    }
    .card-description {
        font-size: 14px;
        margin: 10px 0;
    }
    .card-category {
        font-size: 12px;
        color: #666;
        margin-bottom: 10px;
    }
    .use-button {
        background-color: #4CAF50;
        color: white;
        padding: 5px 10px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
        margin: 5px 0;
        transition-duration: 0.4s;
    }
    .use-button:hover {
        background-color: #45a049;
    }
    .sidebar .stRadio > div {
        flex-direction: column;
    }
</style>
""", unsafe_allow_html=True)

# Função para fazer requisições à API
def api_request(endpoint, method="GET", data=None, params=None):
    base_url = "https://tess.pareto.io/api"  # URL correta da API TESS
    url = f"{base_url}/{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('TESS_API_KEY')}"
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            return {"erro": f"Método {method} não suportado"}
        
        # Verificar status da resposta
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = f"Erro na API: {response.status_code}"
            try:
                error_detail = response.json()
                if isinstance(error_detail, dict) and "detail" in error_detail:
                    error_msg += f" - {error_detail['detail']}"
            except:
                pass
            return {"erro": error_msg}
            
    except Exception as e:
        return {"erro": f"Erro na comunicação com a API: {str(e)}"}

# Função para categorizar agentes baseado na descrição e categoria
def categorizar_agente(descricao, categoria):
    descricao = descricao.lower() if descricao else ""
    categoria = categoria.lower() if categoria else ""
    
    # Mapeamento de palavras-chave para categorias
    mapeamento = {
        "Imagem": ["imagem", "img", "foto", "picture", "image", "dall-e", "stable diffusion", "midjourney"],
        "Chat": ["chat", "conversação", "conversa", "diálogo", "assistente"],
        "Vídeo": ["vídeo", "video", "filme", "animação", "animation"],
        "Dublagem": ["dublagem", "voz", "voice", "áudio", "audio", "som", "sound", "narração"],
        "Código": ["código", "code", "programação", "programming", "developer", "desenvolvedor"],
        "Texto": ["texto", "text", "conteúdo", "content", "escrita", "writing", "gpt"]
    }
    
    # Verificar correspondências
    for tipo, palavras_chave in mapeamento.items():
        for palavra in palavras_chave:
            if palavra in descricao or palavra in categoria:
                return tipo
    
    # Se não encontrar correspondência específica
    return "Texto"  # Categoria padrão

# Sidebar para filtros
st.sidebar.title("Filtros")

# Seleção do tipo de IA
tipo_ia = st.sidebar.radio(
    "Tipo da IA",
    ["Todos", "Imagem", "Texto", "Chat", "Dublagem", "Código", "Vídeo"],
    index=0
)

# Campo de busca
busca = st.sidebar.text_input("Buscar agentes", "")

# Obter lista de agentes
@st.cache_data(ttl=300)  # Cache por 5 minutos
def carregar_agentes():
    resultado = api_request("agents")
    if "erro" in resultado:
        st.error(f"Erro ao carregar agentes: {resultado['erro']}")
        return []
    
    # Verificar estrutura da resposta
    if "data" in resultado:
        # Processar agentes
        agentes = []
        for agente in resultado["data"]:
            tipo_ia = categorizar_agente(agente.get("description", ""), agente.get("category", ""))
            agentes.append({
                "ID": agente.get("id"),
                "Nome": agente.get("name", "Nome não disponível"),
                "Descrição": agente.get("description", "Sem descrição"),
                "Categoria": agente.get("category", "N/A"),
                "Tipo": tipo_ia
            })
        return agentes
    return []

# Título principal
st.title("Filtro de Agentes TESS")

# Carregar agentes
with st.spinner("Carregando agentes..."):
    agentes = carregar_agentes()

# Verificar se há agentes disponíveis
if not agentes or len(agentes) == 0:
    st.warning("Nenhum agente disponível. Verifique sua conexão com a API.")
else:
    # Filtrar agentes
    agentes_filtrados = agentes
    
    # Filtrar por tipo
    if tipo_ia != "Todos":
        agentes_filtrados = [a for a in agentes_filtrados if a.get("Tipo") == tipo_ia]
    
    # Filtrar por busca
    if busca:
        busca_lower = busca.lower()
        agentes_filtrados = [
            a for a in agentes_filtrados 
            if busca_lower in a.get("Nome", "").lower() or 
               busca_lower in a.get("Descrição", "").lower() or
               busca_lower in str(a.get("ID", "")).lower()
        ]
    
    # Mostrar número de resultados
    st.write(f"Encontrados {len(agentes_filtrados)} agentes")
    
    # Exibir agentes em cards
    cols = st.columns(3)
    
    for i, agente in enumerate(agentes_filtrados):
        col = cols[i % 3]
        
        with col:
            # Definir cor baseada no tipo de IA
            tipo_cor = {
                "Imagem": "#4287f5",
                "Texto": "#42f5aa",
                "Chat": "#f542a7",
                "Dublagem": "#f5c242",
                "Código": "#a742f5",
                "Vídeo": "#f54242"
            }
            cor = tipo_cor.get(agente.get("Tipo"), "#42f5aa")
            
            st.markdown(f"""
            <div class="agent-card">
                <div style="
                    display: inline-block;
                    padding: 5px 10px;
                    border-radius: 15px;
                    background-color: {cor};
                    color: white;
                    font-size: 12px;
                    margin-bottom: 10px;
                ">
                    {agente.get("Tipo", "N/A")}
                </div>
                <div class="card-id">ID: {agente.get('ID', 'N/A')}</div>
                <div class="card-title">{agente.get('Nome', 'Sem nome')}</div>
                <div class="card-description">{agente.get('Descrição', 'Sem descrição')}</div>
                <div class="card-category">Categoria: {agente.get('Categoria', 'N/A')}</div>
                <a href="app_tess.py?agent_id={agente.get('ID', '')}" class="use-button">Usar Agente</a>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("Desenvolvido para TESS XTP © 2023")

# Botão para atualizar a lista
if st.sidebar.button("Atualizar Lista de Agentes"):
    st.cache_data.clear()
    st.experimental_rerun()

# Função para gerar URL para integração com app_tess.py
def gerar_url_app_tess(agent_id):
    return f"http://localhost:8501/?agent_id={agent_id}"

# Estilo CSS para a aplicação
def local_css():
    st.markdown("""
    <style>
        .agent-card {
            border-radius: 10px;
            border: 1px solid #ddd;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            position: relative;
            height: 100%;
        }
        .agent-card h3 {
            margin-top: 0;
            margin-bottom: 10px;
        }
        .agent-card p {
            margin-bottom: 5px;
            font-size: 14px;
        }
        .agent-card .agent-id {
            color: #666;
            font-size: 12px;
        }
        .agent-card .agent-category {
            font-style: italic;
            font-size: 12px;
            color: #777;
        }
        .agent-card .agent-description {
            margin-top: 10px;
            margin-bottom: 15px;
            font-size: 14px;
            line-height: 1.4;
            max-height: 100px;
            overflow-y: auto;
        }
        .agent-card .agent-btn {
            display: inline-block;
            padding: 8px 12px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            text-align: center;
            margin-top: 10px;
            font-size: 14px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .agent-card .agent-btn:hover {
            background-color: #45a049;
        }
        .agent-type-badge {
            position: absolute;
            top: 10px;
            right: 10px;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 12px;
            color: white;
        }
        .tipo-Imagem {
            background-color: #1E88E5;
        }
        .tipo-Texto {
            background-color: #43A047;
        }
        .tipo-Chat {
            background-color: #E91E63;
        }
        .tipo-Dublagem {
            background-color: #FFC107;
            color: #333;
        }
        .tipo-Código {
            background-color: #9C27B0;
        }
        .tipo-Vídeo {
            background-color: #F44336;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            font-size: 12px;
            color: #777;
        }
        .highlight {
            background-color: yellow;
            padding: 0 2px;
        }
        @media (max-width: 768px) {
            .agent-card {
                padding: 10px;
            }
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    local_css()
    
    # Título da aplicação
    st.title("Filtro de Agentes TESS")
    st.subheader("Encontre o agente ideal para sua necessidade")
    
    # Inicializar estado da sessão se necessário
    if "agentes" not in st.session_state:
        st.session_state["agentes"] = carregar_agentes()
        
    # Barra lateral para filtros
    with st.sidebar:
        st.header("Filtros")
        
        # Filtro por tipo de IA
        st.subheader("Tipo de IA")
        tipo_ia = st.radio(
            "Selecione o tipo de IA:",
            ["Todos", "Imagem", "Texto", "Chat", "Dublagem", "Código", "Vídeo"]
        )
        
        # Campo de busca
        st.subheader("Busca")
        search_query = st.text_input("Buscar agentes:")
        
        # Botão para atualizar lista de agentes
        if st.button("Atualizar Lista de Agentes"):
            st.cache_data.clear()
            st.session_state["agentes"] = carregar_agentes()
            st.success("Lista de agentes atualizada com sucesso!")
            
        # Informações adicionais
        st.markdown("---")
        st.markdown("### Como utilizar")
        st.markdown("""
        1. Use os filtros para encontrar o agente desejado
        2. Clique em "Usar Agente" para abrir o app TESS
        3. Filtre por texto para buscar funcionalidades específicas
        """)
        
        # Adicionar link para documentação
        st.markdown("---")
        st.markdown("[Ver documentação completa](docs/usando_filtro_agentes.md)")
    
    # Filtrar agentes
    agentes_filtrados = st.session_state["agentes"]
    
    # Aplicar filtro por tipo de IA
    if tipo_ia != "Todos":
        agentes_filtrados = [a for a in agentes_filtrados if a["Tipo"] == tipo_ia]
    
    # Aplicar filtro de busca
    if search_query:
        query_lower = search_query.lower()
        agentes_filtrados = [
            a for a in agentes_filtrados 
            if (
                query_lower in str(a["ID"]).lower() or
                query_lower in a["Nome"].lower() or
                query_lower in a["Descrição"].lower() or
                query_lower in a["Categoria"].lower()
            )
        ]
    
    # Exibir contagem de resultados
    st.write(f"Encontrados **{len(agentes_filtrados)}** agentes.")
    
    # Verificar se há agentes para exibir
    if not agentes_filtrados:
        st.warning("Nenhum agente encontrado com os filtros atuais.")
        st.stop()
    
    # Exibir agentes em cards (3 colunas)
    cols = st.columns(3)
    
    for idx, agente in enumerate(agentes_filtrados):
        col_idx = idx % 3
        
        # Definir cor com base no tipo
        tipo_cor = f"tipo-{agente['Tipo']}"
        
        # Adicionar highlight à descrição se houver busca
        descricao = agente["Descrição"]
        if search_query:
            # Adicionar highlight às palavras da busca
            highlighted_desc = descricao
            for palavra in search_query.split():
                if palavra.lower() in descricao.lower():
                    pattern = re.compile(re.escape(palavra), re.IGNORECASE)
                    highlighted_desc = pattern.sub(f'<span class="highlight">{palavra}</span>', highlighted_desc)
            descricao = highlighted_desc
        
        with cols[col_idx]:
            # Criar card HTML para melhor controle visual
            st.markdown(f"""
            <div class="agent-card">
                <span class="agent-type-badge {tipo_cor}">{agente['Tipo']}</span>
                <h3>{agente['Nome'] if agente['Nome'] else f"Agente {agente['ID']}"}</h3>
                <div class="agent-id">ID: {agente['ID']}</div>
                <div class="agent-category">Categoria: {agente['Categoria']}</div>
                <div class="agent-description">{descricao}</div>
                <a href="{gerar_url_app_tess(agente['ID'])}" target="_blank" class="agent-btn">Usar Agente</a>
            </div>
            """, unsafe_allow_html=True)
    
    # Adicionar footer
    st.markdown("""
    <div class="footer">
        Filtro de Agentes TESS © {datetime.now().year} - Desenvolvido com Streamlit
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 