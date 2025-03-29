#!/bin/bash

# Cores para saída
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Configurando ambiente TESS-MCP com CrewAI ===${NC}"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python3 não encontrado. Por favor, instale o Python 3.8 ou superior.${NC}"
    exit 1
fi

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Criando ambiente virtual...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Erro ao criar ambiente virtual.${NC}"
        exit 1
    fi
fi

# Ativar ambiente virtual
echo -e "${BLUE}Ativando ambiente virtual...${NC}"
source venv/bin/activate

# Instalar dependências
echo -e "${BLUE}Instalando dependências...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro ao instalar dependências.${NC}"
    exit 1
fi

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo -e "${BLUE}Criando arquivo .env a partir do exemplo...${NC}"
    cp .env.example .env
    echo -e "${GREEN}Arquivo .env criado. Por favor, edite-o com suas chaves de API.${NC}"
fi

# Verificar se o servidor MCP está em execução
echo -e "${BLUE}Verificando se o servidor MCP está em execução...${NC}"
curl -s http://localhost:3001/health > /dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}O servidor MCP não parece estar em execução na porta 3001.${NC}"
    echo -e "${RED}Por favor, inicie o servidor MCP antes de continuar.${NC}"
    echo -e "${BLUE}Você pode iniciar o servidor MCP com:${NC}"
    echo -e "    cd .. && npm run start"
else
    echo -e "${GREEN}Servidor MCP detectado na porta 3001.${NC}"
fi

# Perguntar ao usuário o que fazer
echo ""
echo -e "${BLUE}O que você gostaria de fazer?${NC}"
echo "1. Iniciar a interface Streamlit"
echo "2. Apenas configurar o ambiente (já concluído)"
read -p "Escolha (1/2): " choice

if [ "$choice" = "1" ]; then
    echo -e "${BLUE}Iniciando interface Streamlit...${NC}"
    streamlit run app.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}Erro ao iniciar Streamlit.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}Ambiente configurado com sucesso!${NC}"
    echo -e "${BLUE}Para iniciar a interface Streamlit manualmente, execute:${NC}"
    echo -e "    source venv/bin/activate"
    echo -e "    streamlit run app.py"
fi

# Desativar ambiente virtual se não estiver executando Streamlit
if [ "$choice" != "1" ]; then
    deactivate
fi 