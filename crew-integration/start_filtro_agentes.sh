#!/bin/bash

# Script para iniciar o filtro de agentes TESS

# Verificar se o ambiente virtual está ativado
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Verificando ambiente virtual..."
    if [ -d "venv" ]; then
        echo "Ativando ambiente virtual existente..."
        source venv/bin/activate
    else
        echo "Criando e ativando novo ambiente virtual..."
        python -m venv venv
        source venv/bin/activate
    fi
fi

# Instalar dependências necessárias
echo "Verificando dependências..."
pip install -q streamlit requests python-dotenv pandas

# Verificar arquivo .env
if [ ! -f ".env" ]; then
    echo "Arquivo .env não encontrado. Criando exemplo..."
    echo "TESS_API_KEY=sua_chave_api_aqui" > .env
    echo "Adicione sua chave API TESS ao arquivo .env antes de continuar."
fi

# Iniciar aplicativo
echo "Iniciando o aplicativo de filtro de agentes TESS..."
streamlit run filtro_agentes_tess.py 