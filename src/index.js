/**
 * Módulo principal da integração TESS com Crew AI
 * @module crew-ai-tess-pareto
 */

const path = require('path');

/**
 * Exporta as configurações e componentes necessários para a integração
 */
module.exports = {
  /**
   * Configuração do adaptador MCP para TESS
   */
  getMcpConfig: () => {
    return {
      name: 'mcp-server-tess',
      version: '1.0.1',
      description: 'Servidor MCP para integração com TESS',
      tessApiUrl: process.env.TESS_API_URL || 'https://tess.pareto.io/api'
    };
  },

  /**
   * Caminho para o diretório do servidor MCP
   */
  getServerPath: () => {
    return path.resolve(__dirname, '..', 'mcp-server-tess');
  },

  /**
   * Exporta adaptadores e ferramentas específicas
   */
  adapters: require('./adapters'),
  commands: require('./commands'),
  providers: require('./providers'),
  tools: require('./tools'),
  utils: require('./utils')
}; 