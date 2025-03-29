require('dotenv').config();
const express = require('express');
const cors = require('cors');
const extism = require('@extism/extism');
const fs = require('fs');
const path = require('path');
const { TessClient, createTessTools } = require('./src/tess_tools');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3000;
const PLUGIN_PATH = path.join(__dirname, 'target/wasm32-wasip1/release/mcp_server_tess_xtp.wasm');

let plugin = null;
let tessClient = null;
let tessTools = null;

async function initPlugin() {
    // Inicializar cliente TESS
    tessClient = new TessClient(
        process.env.TESS_API_KEY || '',
        process.env.TESS_API_URL || 'https://tess.pareto.io/api'
    );
    
    // Criar ferramentas TESS para MCP
    tessTools = createTessTools(tessClient);
    
    // Adicionar ferramentas TESS à configuração do plugin
    const manifest = {
        wasm: [
            { path: PLUGIN_PATH }
        ],
        config: {
            MCP_API_KEY: process.env.MCP_API_KEY || '',
            MCP_API_URL: process.env.MCP_API_URL || 'https://www.mcp.run/api',
            TESS_API_KEY: process.env.TESS_API_KEY || '',
            TESS_API_URL: process.env.TESS_API_URL || 'https://tess.pareto.io/api',
            TESS_TOOLS: JSON.stringify(Object.keys(tessTools))
        }
    };
    
    plugin = await extism.createPlugin(manifest, { useWasi: true });
}

// Função para processar requisições através do plugin
async function handlePluginRequest(req) {
    // Verificar se é uma requisição para executar uma ferramenta TESS
    if (req.path === '/api/mcp/execute' && req.method === 'POST' && 
        req.body && req.body.tool && req.body.tool.startsWith('tess.')) {
        
        const toolName = req.body.tool;
        const params = req.body.params || {};
        
        if (!tessTools[toolName]) {
            return {
                status: 404,
                body: JSON.stringify({ error: `Ferramenta TESS não encontrada: ${toolName}` }),
                headers: { 'Content-Type': 'application/json' }
            };
        }
        
        try {
            // Executar a ferramenta TESS diretamente
            const result = await tessTools[toolName].handler(params);
            return {
                status: 200,
                body: JSON.stringify(result),
                headers: { 'Content-Type': 'application/json' }
            };
        } catch (error) {
            console.error(`Erro ao executar ferramenta TESS ${toolName}:`, error);
            return {
                status: 500,
                body: JSON.stringify({ error: error.message }),
                headers: { 'Content-Type': 'application/json' }
            };
        }
    }
    
    // Para outras requisições, usar o plugin normalmente
    const request = {
        method: req.method,
        path: req.path,
        body: JSON.stringify(req.body),
        query: req.query,
        headers: req.headers
    };
    
    const result = await plugin.call('handle_request', JSON.stringify(request));
    // Converter DataView para string e depois fazer parse como JSON
    const resultString = new TextDecoder().decode(result);
    return JSON.parse(resultString);
}

// Health check
app.get('/health', async (req, res) => {
    try {
        const response = await handlePluginRequest(req);
        res.status(response.status).json(JSON.parse(response.body));
    } catch (error) {
        console.error('Health check error:', error);
        res.status(500).json({ error: 'Erro interno do servidor' });
    }
});

// Listar ferramentas MCP (adicionando as ferramentas TESS)
app.get('/api/mcp/tools', async (req, res) => {
    try {
        // Obter as ferramentas padrão do MCP
        const response = await handlePluginRequest(req);
        let tools = [];
        
        // Se a resposta for bem-sucedida, extrair as ferramentas
        if (response.status === 200) {
            try {
                const responseBody = JSON.parse(response.body);
                if (responseBody.tools && Array.isArray(responseBody.tools)) {
                    tools = responseBody.tools;
                }
            } catch (e) {
                console.error('Erro ao fazer parse das ferramentas MCP:', e);
            }
        }
        
        // Adicionar ferramentas TESS à lista
        Object.entries(tessTools).forEach(([name, tool]) => {
            tools.push({
                name: name,
                description: tool.description,
                parameters: Object.entries(tool.parameters).map(([paramName, paramConfig]) => ({
                    name: paramName,
                    type: paramConfig.type,
                    description: paramConfig.description,
                    required: !paramConfig.optional,
                    default: paramConfig.default
                }))
            });
        });
        
        // Enviar a lista combinada
        res.status(200).json({ tools });
    } catch (error) {
        console.error('MCP tools error:', error);
        res.status(500).json({ error: 'Erro ao listar ferramentas MCP' });
    }
});

// Executar ferramenta MCP
app.post('/api/mcp/execute', async (req, res) => {
    try {
        const response = await handlePluginRequest(req);
        res.status(response.status)
           .set(response.headers)
           .send(response.body);
    } catch (error) {
        console.error('MCP execute error:', error);
        res.status(500).json({ error: 'Erro ao executar ferramenta MCP' });
    }
});

// Inicializar plugin e iniciar servidor
async function start() {
    try {
        await initPlugin();
        app.listen(PORT, () => {
            console.log(`Servidor TESS-MCP rodando na porta ${PORT}`);
            console.log(`Ferramentas TESS disponíveis: ${Object.keys(tessTools).join(', ')}`);
        });
    } catch (error) {
        console.error('Erro ao inicializar servidor:', error);
        process.exit(1);
    }
}

start(); 