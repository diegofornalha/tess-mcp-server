#!/bin/bash

echo "=== Configurando ambiente TESS-MCP com CrewAI (versão corrigida) ==="

# Criar e ativar ambiente virtual
echo "Ativando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Instalar setuptools primeiro para resolver o problema de pkg_resources
echo "Instalando setuptools para resolver o problema de pkg_resources..."
pip install --upgrade setuptools
pip install --upgrade pip

# Instalar dependências
echo "Instalando dependências..."
pip install -r requirements.txt

# Verificar conexão com o servidor MCP-TESS
echo "Verificando conexão com o servidor MCP-TESS.."
curl -s http://localhost:3001/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Servidor MCP-TESS disponível!"
else
    echo "❌ Servidor MCP-TESS indisponível. Verifique se o servidor está em execução."
fi

# Iniciar aplicação Streamlit
echo "Iniciando aplicação Streamlit..."
streamlit run app.py 