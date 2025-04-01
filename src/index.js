/**
 * Ponto de entrada principal para o servidor TESS-MCP
 * 
 * Este módulo inicializa o servidor MCP e expõe as ferramentas TESS
 */

const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const { createMcpAdapter } = require('./adapters');

// Carregar variáveis de ambiente
dotenv.config();

/**
 * Inicializa o servidor MCP com as ferramentas TESS
 * 
 * @param {Object} config - Configuração do servidor
 * @returns {Object} Servidor MCP configurado
 */
function initializeMcpServer(config = {}) {
  // Mesclar configuração fornecida com variáveis de ambiente
  const serverConfig = {
    PORT: process.env.PORT || 3001,
    TESS_API_KEY: process.env.TESS_API_KEY,
    TESS_API_URL: process.env.TESS_API_URL || 'https://tess.pareto.io/api',
    ...config
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
      version: '1.0.0',
      message: 'Servidor TESS-MCP em execução'
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
  
  // Iniciar servidor
  const server = {
    start: () => {
      return new Promise((resolve) => {
        const httpServer = app.listen(serverConfig.PORT, () => {
          console.log(`Servidor TESS-MCP rodando na porta ${serverConfig.PORT}`);
          resolve(httpServer);
        });
      });
    },
    app,
    adapter: mcpAdapter
  };
  
  return server;
}

// Iniciar servidor se for executado diretamente
if (require.main === module) {
  const server = initializeMcpServer();
  server.start();
}

module.exports = {
  initializeMcpServer
};