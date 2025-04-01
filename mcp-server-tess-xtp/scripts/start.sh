#!/bin/bash
# Script para iniciar o servidor TESS-MCP
# Inspirado no DesktopCommanderMCP

# Caminho para o diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Verificar dependências
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Por favor, instale o Node.js para continuar."
    exit 1
fi

# Instalar dependências se necessário
if [ ! -d "node_modules" ] || [ ! -f "node_modules/.modules-installed" ]; then
    echo "📦 Instalando dependências..."
    npm install
    touch node_modules/.modules-installed
fi

# Verificar arquivo .env
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "🔧 Arquivo .env não encontrado. Criando a partir do .env.example..."
        cp .env.example .env
        echo "⚠️ Por favor, edite o arquivo .env com suas configurações antes de continuar."
        exit 1
    else
        echo "❌ Arquivo .env.example não encontrado. Impossível criar configuração padrão."
        exit 1
    fi
fi

# Verificar se a API Key do TESS está configurada
if ! grep -q "TESS_API_KEY=" .env || grep -q "TESS_API_KEY=$" .env || grep -q "TESS_API_KEY=\"\"" .env; then
    echo "❌ TESS_API_KEY não configurada no arquivo .env."
    echo "⚠️ Por favor, adicione sua API Key do TESS ao arquivo .env."
    exit 1
fi

# Iniciar o servidor
echo "🚀 Iniciando servidor TESS-MCP..."
echo "📌 Pressione Ctrl+C para encerrar."
echo ""

# Executar com nodemon para desenvolvimento, ou node para produção
if [ "$1" = "--prod" ]; then
    node mcp-adapter.js
else
    if command -v nodemon &> /dev/null; then
        echo "🔄 Modo de desenvolvimento ativado (hot-reload)."
        nodemon mcp-adapter.js
    else
        echo "⚠️ Nodemon não encontrado, usando node padrão."
        node mcp-adapter.js
    fi
fi 