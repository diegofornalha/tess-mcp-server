#!/bin/bash

# Script para iniciar o servidor TESS-MCP
# Autor: Arcee CLI Agentes Tess
# Data: $(date +%d/%m/%Y)

# Código de cores para saída
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando servidor TESS-MCP...${NC}"

# Encontra o diretório raiz do projeto (funciona mesmo que o script seja chamado de outro lugar)
get_project_root() {
    # Obtém o caminho do diretório atual do script
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    # Navega um nível acima para chegar ao diretório raiz do projeto
    echo "$(cd "$script_dir/.." && pwd)"
}

PROJECT_ROOT=$(get_project_root)
# Diretório do servidor - suporta caminho fixo ou relativo
SERVIDOR_DIR="${PROJECT_ROOT}/mcp-server-tess"

# Verifica se o diretório existe
if [ ! -d "$SERVIDOR_DIR" ]; then
    echo -e "${RED}❌ Erro: Diretório $SERVIDOR_DIR não encontrado!${NC}"
    exit 1
fi

# Navega para o diretório e prepara para iniciar o servidor
cd "$SERVIDOR_DIR" || exit 1
echo -e "${BLUE}📂 Diretório: $(pwd)${NC}"

# Verifica se o arquivo mcp-adapter.js existe
if [ ! -f "mcp-adapter.js" ]; then
    echo -e "${RED}❌ Erro: Arquivo mcp-adapter.js não encontrado${NC}"
    exit 1
fi

# Verifica se tem o npm instalado
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ Erro: npm não encontrado. Por favor, instale o Node.js e npm.${NC}"
    exit 1
fi

# Instala dependências se node_modules não existir
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Instalando dependências...${NC}"
    npm install
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro ao instalar dependências.${NC}"
        exit 1
    fi
fi

# Inicia o servidor
echo -e "${GREEN}🔄 Iniciando npm start...${NC}"
npm start

# Este código abaixo só será executado se o npm start for interrompido
echo -e "${RED}⚠️ Servidor TESS-MCP foi encerrado.${NC}" 