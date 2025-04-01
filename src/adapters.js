/**
 * Adaptadores para o TESS-MCP
 * 
 * Este módulo fornece adaptadores para integrar o TESS com o protocolo MCP
 */

const { TessClient, createTessTools } = require('./tess_tools');

/**
 * Cria um adaptador MCP para as ferramentas TESS
 * 
 * @param {Object} config - Configuração do servidor
 * @returns {Object} Adaptador MCP com ferramentas TESS
 */
function createMcpAdapter(config) {
  // Inicializar o cliente TESS com as configurações fornecidas
  const tessClient = new TessClient(
    config.TESS_API_KEY,
    config.TESS_API_URL || 'https://tess.pareto.io/api'
  );
  
  // Criar as ferramentas TESS
  const tessTools = createTessTools(tessClient);
  
  // Converter ferramentas TESS para formato MCP
  const mcpTools = Object.entries(tessTools).map(([name, tool]) => {
    return {
      name,
      description: tool.description,
      parameters: Object.entries(tool.parameters).map(([paramName, paramConfig]) => ({
        name: paramName,
        type: paramConfig.type,
        description: paramConfig.description,
        required: !paramConfig.optional,
        default: paramConfig.default
      })),
      handler: tool.handler
    };
  });
  
  return {
    tools: mcpTools,
    execute: async (toolName, params) => {
      const tool = tessTools[toolName];
      if (!tool) {
        throw new Error(`Ferramenta não encontrada: ${toolName}`);
      }
      
      try {
        return await tool.handler(params);
      } catch (error) {
        throw new Error(`Erro ao executar ferramenta ${toolName}: ${error.message}`);
      }
    }
  };
}

module.exports = {
  createMcpAdapter
};