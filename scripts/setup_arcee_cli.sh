#!/bin/bash

echo "=== Configurando Arcee CLI ==="

# Definir cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Caminho para o Arcee CLI já instalado
ARCEE_PATH="/Users/agents/Desktop/studio/MCP-CLI-TESS/arcee_cli/venv/bin/arcee"

# Verificar se o Arcee CLI existe no caminho especificado
if [ ! -f "$ARCEE_PATH" ]; then
    echo -e "${RED}❌ Arcee CLI não encontrado em: $ARCEE_PATH${NC}"
    echo -e "${YELLOW}Verificando se está disponível em outros lugares...${NC}"
    
    # Tentar encontrar o arcee em outros lugares
    ALTERNATIVE_PATH=$(which arcee 2>/dev/null)
    
    if [ -n "$ALTERNATIVE_PATH" ]; then
        echo -e "${GREEN}✅ Arcee CLI encontrado em: $ALTERNATIVE_PATH${NC}"
        ARCEE_PATH=$ALTERNATIVE_PATH
    else
        echo -e "${RED}❌ Arcee CLI não encontrado no sistema.${NC}"
        echo -e "${YELLOW}Você precisa instalar o Arcee CLI para continuar.${NC}"
        exit 1
    fi
fi

# Criar um arquivo .env para armazenar as variáveis de ambiente
ENV_FILE="mcp-server-tess-xtp/crew-integration/.env"

# Verificar se já existe uma API key do Arcee no arquivo .env
if grep -q "ARCEE_API_KEY" "$ENV_FILE"; then
    echo -e "${BLUE}ARCEE_API_KEY já configurada no arquivo .env${NC}"
else
    # Verificar se existe uma API key do Arcee no ambiente
    if [ -z "$ARCEE_API_KEY" ]; then
        echo -e "${YELLOW}⚠️ ARCEE_API_KEY não encontrada no ambiente.${NC}"
        echo -e "${YELLOW}Usando a chave de exemplo do projeto.${NC}"
        
        # Usar a chave de exemplo
        ARCEE_API_KEY="nwrZHj7KOun0iO0PGc0VAWUzDeA7I0eWPKzhjsMUydpun8e5e1v1nXSFz7lMG07HzyPq7cVtL_bCOn-vTLx-4gNAiQo"
    fi
    
    echo -e "${GREEN}Adicionando ARCEE_API_KEY ao arquivo .env${NC}"
    echo "ARCEE_API_KEY=$ARCEE_API_KEY" >> "$ENV_FILE"
    echo "ARCEE_MODEL=auto" >> "$ENV_FILE"
fi

# Criar um link simbólico para o Arcee CLI na pasta local bin
mkdir -p "mcp-server-tess-xtp/crew-integration/bin"
ln -sf "$ARCEE_PATH" "mcp-server-tess-xtp/crew-integration/bin/arcee"

# Adicionar a pasta bin ao PATH dentro do script setup_fix.sh
SETUP_SCRIPT="mcp-server-tess-xtp/crew-integration/setup_fix.sh"

if grep -q "PATH=\$PATH:\$PWD/bin" "$SETUP_SCRIPT"; then
    echo -e "${BLUE}PATH já configurado no setup_fix.sh${NC}"
else
    echo -e "${GREEN}Atualizando setup_fix.sh para incluir o caminho do Arcee CLI${NC}"
    # Fazer backup do arquivo original
    cp "$SETUP_SCRIPT" "${SETUP_SCRIPT}.bak"
    
    # Adicionar linha para incluir o caminho local bin no PATH
    sed -i '' '/#!\/bin\/bash/a\
# Adicionar pasta bin local ao PATH\
export PATH=$PATH:$PWD/bin\
' "$SETUP_SCRIPT"
fi

# Testar se o Arcee CLI está funcionando
echo -e "${YELLOW}Testando Arcee CLI...${NC}"
"$ARCEE_PATH" --help

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Arcee CLI configurado com sucesso!${NC}"
    echo "Comandos disponíveis:"
    "$ARCEE_PATH" --help | grep -A 10 "Commands:"
    echo ""
    echo -e "${BLUE}Para usar o Arcee CLI diretamente:${NC}"
    echo "  mcp-server-tess-xtp/crew-integration/bin/arcee"
    echo ""
    echo -e "${BLUE}Para iniciar a aplicação Streamlit com suporte ao Arcee:${NC}"
    echo "  cd mcp-server-tess-xtp/crew-integration && ./setup_fix.sh"
else
    echo -e "${RED}❌ Erro ao testar o Arcee CLI${NC}"
    echo "Verifique se o arquivo existe e tem permissão de execução"
fi 