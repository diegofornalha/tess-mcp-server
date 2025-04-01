#!/bin/bash
# Script de configuração para o TESS-MCP Server
# Este script instala dependências e configura o ambiente

# Cores para melhor visualização
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo -e "╔════════════════════════════════════════════╗"
echo -e "║           TESS-MCP SERVER SETUP            ║"
echo -e "║                                            ║"
echo -e "║  Configuração do servidor de integração    ║"
echo -e "║      entre TESS e protocolo MCP            ║"
echo -e "╚════════════════════════════════════════════╝"
echo -e "${NC}"

# Função para verificar se um comando existe
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Verificar dependências
echo -e "${YELLOW}Verificando dependências...${NC}"

# Verificar Node.js
if command_exists node; then
  NODE_VERSION=$(node -v)
  echo -e "✅ Node.js encontrado: ${NODE_VERSION}"
  
  # Verificar versão mínima do Node.js (v18+)
  NODE_MAJOR_VERSION=$(echo $NODE_VERSION | cut -d. -f1 | tr -d 'v')
  if [ "$NODE_MAJOR_VERSION" -lt 18 ]; then
    echo -e "${RED}⚠️  Versão do Node.js muito antiga. É recomendado usar v18 ou superior.${NC}"
    
    # Perguntar ao usuário se ele deseja continuar
    read -p "Deseja continuar com a versão atual do Node.js? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
      echo -e "${RED}Configuração cancelada. Por favor, atualize o Node.js e tente novamente.${NC}"
      exit 1
    fi
  fi
else
  echo -e "${RED}❌ Node.js não encontrado. Por favor, instale o Node.js v18 ou superior.${NC}"
  echo -e "Você pode baixar em: https://nodejs.org/"
  exit 1
fi

# Verificar npm
if command_exists npm; then
  NPM_VERSION=$(npm -v)
  echo -e "✅ npm encontrado: ${NPM_VERSION}"
else
  echo -e "${RED}❌ npm não encontrado. Por favor, instale o npm.${NC}"
  exit 1
fi

# Verificar git (opcional, mas útil)
if command_exists git; then
  GIT_VERSION=$(git --version | cut -d' ' -f3)
  echo -e "✅ Git encontrado: ${GIT_VERSION}"
else
  echo -e "${YELLOW}⚠️  Git não encontrado. Não é obrigatório, mas é recomendado para controle de versão.${NC}"
fi

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
  echo -e "${YELLOW}Criando arquivo .env...${NC}"
  cat > .env << EOF
# Configuração do TESS-MCP Server
# Preencha com suas credenciais e configurações

# Chave de API TESS (obrigatória)
TESS_API_KEY=sua_chave_api_aqui

# URL da API TESS (opcional, valor padrão abaixo)
TESS_API_URL=https://tess.pareto.io/api

# Porta para o servidor MCP (opcional, padrão: 3001)
PORT=3001
EOF
  echo -e "✅ Arquivo .env criado. Por favor, edite-o com suas credenciais."
else
  echo -e "✅ Arquivo .env já existe."
fi

# Instalar dependências
echo -e "${YELLOW}Instalando dependências...${NC}"
npm install
if [ $? -eq 0 ]; then
  echo -e "✅ Dependências instaladas com sucesso."
else
  echo -e "${RED}❌ Falha ao instalar dependências. Verifique os erros acima.${NC}"
  exit 1
fi

# Verificar instalação do Smithery CLI (opcional)
echo -e "${YELLOW}Verificando Smithery CLI...${NC}"
if command_exists smithery || npx @smithery/cli@latest --version >/dev/null 2>&1; then
  echo -e "✅ Smithery CLI disponível."
else
  echo -e "${YELLOW}⚠️  Smithery CLI não encontrado. Instalando globalmente...${NC}"
  npm install -g @smithery/cli
  if [ $? -eq 0 ]; then
    echo -e "✅ Smithery CLI instalado globalmente."
  else
    echo -e "${YELLOW}⚠️  Aviso: Smithery CLI não pôde ser instalado globalmente.${NC}"
    echo -e "${YELLOW}   Você ainda pode usá-lo com 'npx @smithery/cli@latest'.${NC}"
  fi
fi

# Tornar scripts executáveis
echo -e "${YELLOW}Tornando scripts executáveis...${NC}"
chmod +x ./scripts/*.sh
echo -e "✅ Scripts configurados."

# Finalizar
echo -e "${GREEN}Configuração concluída com sucesso!${NC}"
echo -e "${BLUE}Para iniciar o servidor:${NC}"
echo -e "  npm start         - Modo normal"
echo -e "  npm run dev       - Modo desenvolvimento (com reinício automático)"
echo -e "  npm run yolo      - Modo automático (sem confirmações)"
echo -e ""
echo -e "${BLUE}Para publicar no Smithery:${NC}"
echo -e "  npm run smithery:build   - Preparar para publicação"
echo -e "  npm run smithery:publish - Publicar no registro Smithery"
echo -e ""
echo -e "${YELLOW}IMPORTANTE: Não esqueça de editar o arquivo .env com sua chave de API TESS!${NC}"