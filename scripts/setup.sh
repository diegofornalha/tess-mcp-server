#!/bin/bash
# Script de configuração para o TESS-MCP
# Inspirado no DesktopCommanderMCP

set -e  # Interrompe o script se algum comando falhar

# Caminho para o diretório do projeto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "======================================================"
echo "🔧 Configuração do Servidor TESS-MCP"
echo "======================================================"
echo ""

# Verificar Node.js
echo "📋 Verificando Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Por favor, instale o Node.js antes de continuar."
    echo "   Acesse https://nodejs.org para baixar e instalar."
    exit 1
fi

NODE_VERSION=$(node -v)
echo "✅ Node.js encontrado: $NODE_VERSION"

# Verificar NPM
echo "📋 Verificando NPM..."
if ! command -v npm &> /dev/null; then
    echo "❌ NPM não encontrado. Por favor, instale o NPM antes de continuar."
    exit 1
fi

NPM_VERSION=$(npm -v)
echo "✅ NPM encontrado: $NPM_VERSION"

# Instalar dependências
echo "📦 Instalando dependências do projeto..."
npm install

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo "📝 Criando arquivo .env a partir do .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Arquivo .env criado com sucesso."
    else
        echo "❌ Arquivo .env.example não encontrado. Criando arquivo .env básico..."
        cat > .env << EOF
# Configurações do servidor TESS-MCP
PORT=3001

# Chave de API do TESS (obrigatória)
TESS_API_KEY=""

# URL da API do TESS (opcional)
TESS_API_URL="https://tess.pareto.io/api"

# Configurações extras (opcionais)
LOG_LEVEL="info"
EOF
        echo "✅ Arquivo .env básico criado."
    fi
    
    echo ""
    echo "⚠️ IMPORTANTE: Você precisa configurar sua TESS_API_KEY no arquivo .env"
    echo "   Edite o arquivo .env antes de iniciar o servidor."
    echo ""
fi

# Verificar diretório public
if [ ! -d "public" ]; then
    echo "📁 Criando diretório public..."
    mkdir -p public
    
    # Criar um arquivo HTML de exemplo
    cat > public/index.html << EOF
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TESS-MCP Cliente</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: #f8f9fa;
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #0066cc;
            padding-bottom: 10px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        pre {
            background: #f4f4f4;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
        button {
            background: #0066cc;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background: #0055aa;
        }
        #output {
            margin-top: 20px;
            padding: 15px;
            background: #f8f8f8;
            border-radius: 4px;
            border-left: 4px solid #0066cc;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Cliente TESS-MCP</h1>
        <p>Este é um cliente básico para testar o servidor TESS-MCP.</p>
        
        <h2>Ferramentas Disponíveis</h2>
        <button id="listTools">Listar Ferramentas</button>
        
        <h2>Testar Execute Agent</h2>
        <div>
            <label for="agentId">ID do Agente:</label>
            <input type="text" id="agentId" placeholder="Ex: 123">
        </div>
        <div>
            <label for="inputText">Texto de Entrada:</label>
            <textarea id="inputText" rows="4" placeholder="Digite o texto de entrada para o agente"></textarea>
        </div>
        <button id="executeAgent">Executar Agente</button>
        
        <div id="output">Os resultados aparecerão aqui...</div>
    </div>

    <script src="/socket.io/socket.io.js"></script>
    <script>
        // Conectar ao WebSocket
        const socket = io();
        const output = document.getElementById('output');
        
        // Exibir mensagem quando conectado
        socket.on('connect', () => {
            output.innerHTML = '<p>Conectado ao servidor TESS-MCP</p>';
        });
        
        // Botão para listar ferramentas
        document.getElementById('listTools').addEventListener('click', () => {
            output.innerHTML = '<p>Solicitando lista de ferramentas...</p>';
            socket.emit('list_tools');
        });
        
        // Receber lista de ferramentas
        socket.on('tools_list', (data) => {
            let html = '<h3>Ferramentas Disponíveis:</h3><ul>';
            data.tools.forEach(tool => {
                html += `<li><strong>${tool.name}</strong>: ${tool.description}</li>`;
            });
            html += '</ul>';
            output.innerHTML = html;
        });
        
        // Botão para executar agente
        document.getElementById('executeAgent').addEventListener('click', () => {
            const agentId = document.getElementById('agentId').value;
            const inputText = document.getElementById('inputText').value;
            
            if (!agentId || !inputText) {
                output.innerHTML = '<p style="color: red">Erro: ID do agente e texto de entrada são obrigatórios</p>';
                return;
            }
            
            output.innerHTML = '<p>Executando agente...</p>';
            socket.emit('call_tool', {
                name: 'tess.execute_agent',
                arguments: {
                    agent_id: agentId,
                    input_text: inputText,
                    wait_execution: false
                }
            });
        });
        
        // Receber resultado da ferramenta
        socket.on('tool_result', (data) => {
            if (data.isError) {
                output.innerHTML = `<p style="color: red">Erro: ${data.error}</p>`;
            } else {
                output.innerHTML = '<h3>Resultado:</h3><pre>' + JSON.stringify(data.result, null, 2) + '</pre>';
            }
        });
        
        // Receber atualizações de execução
        socket.on('execution_update', (data) => {
            const currentOutput = output.innerHTML;
            output.innerHTML = currentOutput + '<p>Atualização: Status = ' + data.status + '</p>';
        });
        
        // Receber conclusão de execução
        socket.on('execution_complete', (data) => {
            output.innerHTML = '<h3>Execução Concluída:</h3><pre>' + JSON.stringify(data.data, null, 2) + '</pre>';
        });
        
        // Receber erros
        socket.on('error', (data) => {
            output.innerHTML = `<p style="color: red">Erro: ${data.message}</p>`;
        });
    </script>
</body>
</html>
EOF
    echo "✅ Página de exemplo criada em public/index.html."
fi

# Tornar scripts executáveis
echo "🔑 Tornando scripts executáveis..."
chmod +x scripts/*.sh

echo ""
echo "======================================================"
echo "✅ Configuração concluída com sucesso!"
echo ""
echo "Para iniciar o servidor, execute:"
echo "  ./scripts/start.sh"
echo ""
echo "Para iniciar em modo produção (sem hot-reload):"
echo "  ./scripts/start.sh --prod"
echo "======================================================" 