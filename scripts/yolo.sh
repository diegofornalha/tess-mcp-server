#!/bin/bash
# Script para executar comandos em modo automático
# Modo "YOLO" - executa sem confirmações

# Define cores para saída
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 MODO YOLO ATIVADO${NC}"
echo -e "${YELLOW}Todos os comandos serão executados automaticamente${NC}"
echo -e "${YELLOW}Use Ctrl+C para sair${NC}\n"

# Executa o comando passado como argumento
if [ $# -gt 0 ]; then
    echo -e "${GREEN}Executando:${NC} $@"
    eval "$@"
    exit $?
fi

# Modo interativo se nenhum comando foi passado
echo -e "${GREEN}Modo interativo. Digite 'exit' para sair.${NC}"
while true; do
    read -p "> " cmd
    
    if [ "$cmd" = "exit" ]; then
        echo "Saindo do modo YOLO..."
        break
    fi
    
    echo -e "${GREEN}Executando:${NC} $cmd"
    eval "$cmd"
done