#!/bin/bash

# Script para iniciar a aplicação Streamlit de geração de anúncios TESS

echo "Iniciando o Gerador de Anúncios com TESS API..."

# Verifica se o ambiente virtual existe
if [ -d "venv" ]; then
    # Ativa o ambiente virtual
    echo "Ativando ambiente virtual..."
    source venv/bin/activate
else
    echo "Ambiente virtual não encontrado. Criando novo ambiente..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Instala as dependências necessárias
    echo "Instalando dependências..."
    pip install -r requirements.txt
    
    # Adiciona pacotes específicos para a aplicação TESS
    pip install streamlit pandas
fi

# Verifica se há arquivo .env
if [ ! -f ".env" ]; then
    echo "Arquivo .env não encontrado. Crie um arquivo .env com a chave da API TESS."
    echo "Exemplo:"
    echo "TESS_API_KEY=sua_chave_api_tess"
    exit 1
fi

# Verifica se pandas está instalado
if ! pip list | grep -q "pandas"; then
    echo "Instalando pandas..."
    pip install pandas
fi

# Verifica se streamlit está instalado
if ! pip list | grep -q "streamlit"; then
    echo "Instalando streamlit..."
    pip install streamlit
fi

# Inicia a aplicação Streamlit
echo "Iniciando aplicação Streamlit..."
streamlit run app_tess.py 