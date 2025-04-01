import streamlit as st
import requests
import json
from datetime import datetime
import os
import time
import logging
import sys
from dotenv import load_dotenv

from tess_crew import TessCrew

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tess_server.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("tess-crew-app")

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da página Streamlit
st.set_page_config(
    page_title="Arcee CLI - Interface Web",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicializar estado da sessão para histórico
if "history" not in st.session_state:
    st.session_state.history = []

# Inicializar TessCrew se não existir
if "crew" not in st.session_state:
    try:
        # Inicializar TessCrew
        st.session_state.crew = TessCrew()
        
        # Log de informações sobre o provedor Arcee
        logger.info(f"Arcee Provider disponível: {st.session_state.crew.arcee_provider.is_available()}")
        
    except Exception as e:
        logger.error(f"Erro ao inicializar TessCrew: {str(e)}", exc_info=True)
        st.error(f"Erro ao inicializar o sistema: {str(e)}")

# Título principal
st.title("🤖 Arcee CLI Web")

# Criar abas simplificadas: apenas Arcee CLI e Ajuda
tab_arcee_cli, tab_ajuda = st.tabs(["Arcee CLI", "Ajuda"])

# Aba principal - Arcee CLI
with tab_arcee_cli:
    st.subheader("🤖 Chat com Arcee AI - Modo AUTO")
    
    st.markdown("""
    Este chat utiliza o modo AUTO para selecionar automaticamente o melhor modelo com base no conteúdo e contexto da sua pergunta.
    """)
    
    # Verificar se o Arcee está disponível
    arcee_available = "crew" in st.session_state and st.session_state.crew.arcee_provider.is_available()
    
    if not arcee_available:
        st.warning("Arcee CLI não está disponível. Verifique se a API key está configurada ou se a CLI está instalada.")
        st.info("Execute o script setup_arcee_cli.sh para configurar o Arcee CLI")
    else:
        with st.form("arcee_query_form"):
            arcee_query = st.text_area("Digite sua consulta (ou 'ajuda' para ver os comandos disponíveis):", height=150)
            
            # Configurações do modelo Arcee (apenas temperatura)
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("**Modo AUTO ativado - seleção dinâmica de modelo**")
                
            with col2:
                arcee_temperature = st.slider(
                    "Temperatura:", 
                    min_value=0.0, 
                    max_value=1.0, 
                    value=0.7, 
                    step=0.1,
                    help="Valores mais baixos = mais determinístico, valores mais altos = mais criativo"
                )
            
            arcee_submitted = st.form_submit_button("Enviar", use_container_width=True)
        
        # Processamento da consulta Arcee
        if arcee_submitted:
            if not arcee_query:
                st.warning("Por favor, digite uma consulta.")
            else:
                # Verificar se é um comando especial
                if arcee_query.strip().lower() == "ajuda":
                    # Mostrar informações de ajuda diretamente, semelhante ao CLI
                    st.success("Comando de ajuda reconhecido")
                    
                    st.markdown("### Comandos Disponíveis")
                    
                    st.markdown("**Comandos gerais:**")
                    st.markdown("""
                    • ajuda - Mostra esta mensagem
                    • limpar - Limpa o histórico da conversa
                    • sair - Encerra o chat
                    • modelos - Mostra estatísticas dos modelos usados no modo AUTO
                    """)
                    
                    st.markdown("**Comandos TESS API:**")
                    st.markdown("""
                    • test_api_tess listar - Lista agentes TESS disponíveis
                    • test_api_tess executar <id> <mensagem> - Executa um agente TESS específico
                    """)
                    
                    st.markdown("**Dicas de uso:**")
                    st.markdown("""
                    • Para tarefas criativas, use frases como 'criar', 'escrever' ou 'imaginar'
                    • Para consultas técnicas, seja específico sobre tecnologias
                    """)
                    
                    # Adicionar ao histórico
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.history.append({
                        "timestamp": timestamp,
                        "query": "ajuda",
                        "result": "Comandos de ajuda exibidos",
                        "provider": "Arcee CLI",
                    })
                
                elif arcee_query.strip().lower() == "test_api_tess listar":
                    # Mostrar lista de agentes TESS
                    st.info("Executando comando TESS: listar agentes...")
                    
                    # Simular resposta mostrando agentes TESS 
                    # (Na implementação real, isso seria buscado da API TESS)
                    st.markdown("### Agentes TESS disponíveis:")
                    
                    st.markdown("""
                    1. Anúncios de Texto no Google Ads para a Marca
                       ID: anuncios-de-texto-no-google-ads-para-a-marca-PefqXk
                       Use a Tess AI para criar anúncios incríveis para suas campanhas da marca no Google

                    2. Anúncios de Texto para Produtos e Serviços
                       ID: anuncios-de-texto-para-produtos-e-servicos-PQskS8
                       Crie anúncios incríveis para suas campanhas de produtos ou serviços no Google Ads

                    3. Anúncios de Performance Max
                       ID: anuncios-de-performance-max-eN50fQ
                       Crie anúncios incríveis para suas campanhas de Performance Max no Google Ads

                    4. Títulos de e-mail chamativos com emoji
                       ID: titulos-de-e-mail-chamativos-com-emoji-d9XY2D
                       Com a Tess AI, crie títulos audaciosos para maximizar a taxa de abertura de e-mails.

                    5. Título de Email para anúncio de novo recurso
                       ID: titulo-de-email-para-anuncio-de-novo-recurso-fDba8a
                       Deixe a Tess AI criar títulos incríveis de email para seu lançamento de novas features
                       
                    Total: 642 agentes disponíveis
                    """)
                    
                    # Adicionar ao histórico
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.history.append({
                        "timestamp": timestamp,
                        "query": "test_api_tess listar",
                        "result": "Lista de agentes TESS exibida",
                        "provider": "Arcee CLI",
                    })
                    
                else:
                    # Processar consulta normal usando Arcee
                    with st.spinner("Processando sua consulta com Arcee..."):
                        try:
                            # Forçar o uso do provedor Arcee
                            original_provider = st.session_state.crew.chat_provider
                            st.session_state.crew.chat_provider = st.session_state.crew.arcee_provider
                            
                            # Processar a consulta
                            start_time = time.time()
                            result = st.session_state.crew.execute_single_query(
                                query=arcee_query,
                                model="auto",  # Arcee sempre usa "auto"
                                temperature=arcee_temperature
                            )
                            end_time = time.time()
                            
                            # Restaurar provedor original
                            st.session_state.crew.chat_provider = original_provider
                            
                            response_text = result.get("response", "")
                            model_used = result.get("model", "desconhecido")
                            
                            # Adicionar ao histórico
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            
                            st.session_state.history.append({
                                "timestamp": timestamp,
                                "query": arcee_query,
                                "result": response_text,
                                "model": model_used,
                                "temperature": arcee_temperature,
                                "provider": "Arcee CLI",
                            })
                            
                            # Exibir modelo usado e resultado
                            st.success(f"✓ Resposta processada com Arcee AI (Modelo: {model_used})")
                            
                            # Exibir o resultado final
                            st.markdown("### Resposta:")
                            st.markdown(response_text)
                            st.caption(f"Tempo de resposta: {end_time - start_time:.2f}s")
                        
                        except Exception as e:
                            st.error(f"Erro ao processar a consulta via Arcee: {str(e)}")
                            logger.error(f"Erro ao processar consulta via Arcee: {str(e)}", exc_info=True)

# Aba de Ajuda
with tab_ajuda:
    st.subheader("Ajuda do Arcee CLI")
    
    st.markdown("### 🤖 Chat com Arcee AI - Modo AUTO")
    
    st.markdown("""
    O Arcee AI é uma interface para comunicação com serviços de inteligência artificial, 
    com seleção automática inteligente do modelo mais adequado para cada consulta.
    """)
    
    st.markdown("### Comandos Disponíveis")
    
    st.markdown("**Comandos gerais:**")
    st.markdown("""
    • ajuda - Mostra esta mensagem
    • limpar - Limpa o histórico da conversa
    • sair - Encerra o chat
    • modelos - Mostra estatísticas dos modelos usados no modo AUTO
    """)
    
    st.markdown("**Comandos TESS API:**")
    st.markdown("""
    • test_api_tess listar - Lista agentes TESS disponíveis
    • test_api_tess executar <id> <mensagem> - Executa um agente TESS específico
    """)
    
    st.markdown("**Dicas de uso:**")
    st.markdown("""
    • Para tarefas criativas, use frases como 'criar', 'escrever' ou 'imaginar'
    • Para consultas técnicas, seja específico sobre tecnologias
    """)
    
    st.markdown("### Como funciona o Modo AUTO?")
    
    st.markdown("""
    No modo AUTO, o Arcee seleciona automaticamente o melhor modelo disponível com base em:
    
    1. **Complexidade da consulta** - Perguntas mais complexas são direcionadas para modelos mais potentes
    2. **Tipo de tarefa** - Tarefas criativas ou técnicas podem ser enviadas para modelos especializados
    3. **Disponibilidade** - Se um modelo não estiver disponível, o sistema faz fallback para alternativas
    
    A temperatura ajusta o equilíbrio entre respostas determinísticas (temperatura baixa) 
    e respostas criativas (temperatura alta).
    """)
    
    st.markdown("### Configuração")
    
    st.markdown("""
    Para configurar o Arcee CLI:
    
    1. Execute o script `./scripts/setup_arcee_cli.sh` na raiz do projeto
    2. Verifique se a instalação foi bem sucedida
    3. Reinicie esta aplicação se necessário
    
    O script vai configurar o Arcee CLI e prepará-lo para uso nesta aplicação.
    """)

# Exibir histórico
if st.session_state.history:
    st.divider()
    st.subheader("📜 Histórico de consultas")
    
    for i, item in enumerate(reversed(st.session_state.history)):
        with st.expander(f"{item.get('timestamp', 'N/A')} - {item.get('query', '')[:50]}{'...' if len(item.get('query', '')) > 50 else ''}"):
            st.markdown(f"**Consulta:**")
            st.markdown(item.get("query", ""))
            
            st.markdown(f"**Resposta:**")
            st.markdown(item.get("result", ""))
            
            # Exibir metadados
            st.markdown("**Detalhes:**")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Provedor:** {item.get('provider', 'Desconhecido')}")
                st.markdown(f"**Modelo:** {item.get('model', 'Desconhecido')}")
            with col2:
                st.markdown(f"**Temperatura:** {item.get('temperature', 'N/A')}")
                st.markdown(f"**Timestamp:** {item.get('timestamp', 'N/A')}")

# Rodapé com informações de versão
st.caption("Arcee CLI Web v1.0.0 | Desenvolvido com Streamlit e CrewAI") 