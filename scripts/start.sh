#!/bin/bash
# Script para iniciar o servidor TESS-MCP
# Este script inicia o servidor e fornece opções para diferentes modos

# Cores para melhor visualização
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo -e "╔════════════════════════════════════════════╗"
echo -e "║           TESS-MCP SERVER START            ║"
echo -e "╚════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
  echo -e "${YELLOW}Arquivo .env não encontrado. Criando a partir do exemplo...${NC}"
  cp .env.example .env
  echo -e "${RED}⚠️  IMPORTANTE: Edite o arquivo .env e adicione sua chave API TESS!${NC}"
fi

# Função para verificar dependências
verify_dependencies() {
  echo -e "${YELLOW}Verificando dependências...${NC}"
  if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Instalando dependências...${NC}"
    npm install
  else
    echo -e "${GREEN}Dependências já instaladas.${NC}"
  fi
}

# Verificar dependências
verify_dependencies

# Determinar o modo de execução
MODE="normal"
DEV_MODE=false

# Processar argumentos
while [[ $# -gt 0 ]]; do
  case $1 in
    --dev)
      MODE="development"
      DEV_MODE=true
      shift
      ;;
    --debug)
      MODE="debug"
      NODE_ENV="development"
      export DEBUG="*"
      shift
      ;;
    *)
      echo -e "${RED}Opção desconhecida: $1${NC}"
      exit 1
      ;;
  esac
done

# Iniciar servidor no modo apropriado
echo -e "${GREEN}Iniciando servidor TESS-MCP em modo ${MODE}...${NC}"

if [ "$DEV_MODE" = true ]; then
  echo -e "${YELLOW}Usando nodemon para reinício automático${NC}"
  npx nodemon src/index.js
else
  node src/index.js
fi 