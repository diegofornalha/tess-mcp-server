#!/bin/bash
# Script para iniciar a aplicação Streamlit do Crew Integration
# Autor: Arcee CLI Agentes Tess
# Data: $(date +%d/%m/%Y)

# Cores para saída
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando aplicação Streamlit do Crew Integration...${NC}"

# Diretório da aplicação
APP_DIR="/Users/agents/Desktop/crew_ai_tess_pareto/mcp-server-tess-xtp/crew-integration"

# Verifica se o diretório existe
if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}❌ Erro: Diretório $APP_DIR não encontrado!${NC}"
    exit 1
fi

# Navega para o diretório e inicia a aplicação
cd "$APP_DIR"
echo -e "${BLUE}📂 Diretório: $(pwd)${NC}"

# Verifica se o ambiente virtual existe e ativa-o
if [ -d "venv" ]; then
    echo -e "${BLUE}🔄 Ativando ambiente virtual...${NC}"
    source venv/bin/activate
else
    echo -e "${BLUE}⚠️ Ambiente virtual não encontrado. Criando...${NC}"
    python -m venv venv
    source venv/bin/activate
    
    echo -e "${BLUE}📦 Instalando dependências...${NC}"
    pip install -r requirements.txt
fi

# Verifica se a CLI Arcee está instalada
if ! command -v arcee &> /dev/null; then
    echo -e "${BLUE}⚠️ CLI Arcee não encontrada. Instalando...${NC}"
    pip install arcee-cli
fi

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo -e "${BLUE}📄 Criando arquivo .env a partir do exemplo...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ Arquivo .env criado. Por favor, edite-o com suas chaves de API.${NC}"
fi

# Verificar se o servidor MCP está em execução
echo -e "${BLUE}🔍 Verificando se o servidor MCP-TESS está em execução...${NC}"
curl -s http://localhost:3001/health > /dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️ Servidor MCP-TESS não detectado. Iniciando automaticamente...${NC}"
    
    # Obter o caminho do script iniciar_tess_mcp_prod.sh
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
    
    # Verifica se o script existe
    if [ -f "$PROJECT_ROOT/scripts/iniciar_tess_mcp_prod.sh" ]; then
        # Inicia o servidor em segundo plano
        bash "$PROJECT_ROOT/scripts/iniciar_tess_mcp_prod.sh" &
        
        # Aguarda 5 segundos para o servidor iniciar
        echo -e "${YELLOW}Aguardando o servidor iniciar (5 segundos)...${NC}"
        sleep 5
        
        # Verifica novamente se o servidor está funcionando
        curl -s http://localhost:3001/health > /dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Servidor MCP-TESS iniciado com sucesso!${NC}"
        else
            echo -e "${RED}⚠️ Não foi possível iniciar o servidor MCP-TESS.${NC}"
            echo -e "${YELLOW}Tentando continuar mesmo assim...${NC}"
        fi
    else
        echo -e "${RED}❌ Script de início do servidor não encontrado.${NC}"
        echo -e "${YELLOW}Caminho buscado: $PROJECT_ROOT/scripts/iniciar_tess_mcp_prod.sh${NC}"
    fi
else
    echo -e "${GREEN}✅ Servidor MCP-TESS detectado na porta 3001.${NC}"
fi

echo -e "${BLUE}🔄 Iniciando Streamlit...${NC}"
python -m streamlit run app.py

# Este código abaixo só será executado se o Streamlit for interrompido
echo -e "${RED}⚠️ Aplicação Streamlit foi encerrada.${NC}"

# Desativa o ambiente virtual
deactivate 