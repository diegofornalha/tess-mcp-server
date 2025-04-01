#!/usr/bin/env node
/**
 * TESS-MCP Server
 * Servidor MCP para integração com a API TESS
 */

const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const { createMcpAdapter } = require('./adapters');

// Carregar variáveis de ambiente
dotenv.config();

/**
 * Inicializa o servidor MCP
 * @param {Object} config - Configuração do servidor
 * @returns {Object} Servidor Express configurado
 */
function createServer(config = {}) {
  // Mesclar configuração fornecida com variáveis de ambiente
  const serverConfig = {
    PORT: process.env.PORT || config.PORT || 3001,
    TESS_API_KEY: process.env.TESS_API_KEY || config.TESS_API_KEY,
    TESS_API_URL: process.env.TESS_API_URL || config.TESS_API_URL || 'https://tess.pareto.io/api'
  };
  
  // Verificar se a chave API foi fornecida
  if (!serverConfig.TESS_API_KEY) {
    throw new Error('TESS_API_KEY é obrigatória. Defina no arquivo .env ou forneça na configuração.');
  }
  
  // Criar adaptador MCP
  const mcpAdapter = createMcpAdapter(serverConfig);
  
  // Configurar servidor Express
  const app = express();
  app.use(cors());
  app.use(express.json());
  
  // Rota de saúde
  app.get('/health', (req, res) => {
    res.json({
      status: 'ok',
      version: '1.0.1',
      message: 'TESS-MCP Server em execução'
    });
  });
  
  // Rota MCP para listar ferramentas
  app.post('/tools/list', (req, res) => {
    try {
      res.json({ tools: mcpAdapter.tools });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });
  
  // Rota MCP para chamar ferramentas
  app.post('/tools/call', async (req, res) => {
    try {
      const { name, arguments: args } = req.body;
      
      if (!name) {
        return res.status(400).json({
          content: [{ type: 'text', text: 'O nome da ferramenta é obrigatório' }],
          isError: true
        });
      }
      
      try {
        const result = await mcpAdapter.execute(name, args || {});
        
        res.json({
          content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
          isError: false
        });
      } catch (error) {
        res.status(500).json({
          content: [{ type: 'text', text: error.message }],
          isError: true
        });
      }
    } catch (error) {
      res.status(500).json({
        content: [{ type: 'text', text: `Erro interno: ${error.message}` }],
        isError: true
      });
    }
  });
  
  return app;
}

/**
 * Função principal para iniciar o servidor
 */
function main() {
  try {
    const app = createServer();
    const PORT = process.env.PORT || 3001;
    
    app.listen(PORT, () => {
      console.log(`Servidor TESS-MCP rodando na porta ${PORT}`);
    });
  } catch (error) {
    console.error(`Erro ao iniciar servidor: ${error.message}`);
    process.exit(1);
  }
}

// Iniciar o servidor se este arquivo for executado diretamente
if (require.main === module) {
  main();
}

// Exportar as funções para uso como módulo
module.exports = createServer;