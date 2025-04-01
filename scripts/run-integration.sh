#!/bin/bash
# Script para executar a demonstração de integração TESS-MCP

# Caminho para o diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "======================================================"
echo "🧩 Demonstração de Integração TESS-MCP"
echo "======================================================"
echo ""

# Verificar se o servidor TESS-MCP está rodando
echo "📋 Verificando se o servidor TESS-MCP está rodando..."

# Tenta fazer uma requisição para o endpoint de saúde
if ! curl -s http://localhost:3001/health > /dev/null; then
    echo "❌ Servidor TESS-MCP não está rodando na porta 3001."
    echo ""
    
    # Pergunta se quer iniciar o servidor
    read -p "Deseja iniciar o servidor TESS-MCP agora? (s/n): " start_server
    
    if [ "$start_server" = "s" ]; then
        echo "🚀 Iniciando servidor TESS-MCP em segundo plano..."
        
        # Inicia o servidor em segundo plano
        (cd "$PROJECT_DIR" && ./scripts/start.sh > /tmp/tess-mcp-server.log 2>&1) &
        
        # Armazena o PID do processo
        SERVER_PID=$!
        
        # Aguarda o servidor iniciar
        echo "⏳ Aguardando o servidor iniciar..."
        sleep 5
        
        # Verifica novamente se o servidor está rodando
        if ! curl -s http://localhost:3001/health > /dev/null; then
            echo "❌ Falha ao iniciar o servidor TESS-MCP."
            echo "   Verifique o log em /tmp/tess-mcp-server.log"
            exit 1
        else
            echo "✅ Servidor TESS-MCP iniciado com sucesso (PID: $SERVER_PID)."
            echo "   Para encerrar o servidor, execute: kill $SERVER_PID"
        fi
    else
        echo "❌ Não é possível executar a demonstração sem o servidor TESS-MCP."
        echo "   Inicie o servidor primeiro com: ./scripts/start.sh"
        exit 1
    fi
else
    echo "✅ Servidor TESS-MCP está rodando."
fi

echo ""
echo "🚀 Iniciando demonstração de integração..."
echo ""

# Executa o script de integração
node scripts/integration.js

# Código de saída
exit_code=$?

echo ""
echo "======================================================"
if [ $exit_code -eq 0 ]; then
    echo "✅ Demonstração concluída com sucesso!"
else
    echo "❌ Demonstração encerrada com erro (código $exit_code)."
fi
echo "======================================================" 