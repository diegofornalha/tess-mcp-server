#!/bin/bash

# Script para executar a aplicação Streamlit TESS-MCP

# Verificar se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python3 não encontrado. Por favor, instale o Python 3 antes de continuar."
    exit 1
fi

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "Instalando dependências..."
pip install -r requirements.txt

# Executar aplicação
echo "Iniciando aplicação Streamlit..."
streamlit run app.py 