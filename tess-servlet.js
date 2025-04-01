/**
 * TESS Servlet para mcp.run
 * 
 * Este arquivo define o servlet TESS para ser publicado no mcp.run.
 * Expõe as funcionalidades da API TESS como ferramentas MCP portáveis.
 */

const { TessClient } = require('./src/tess_tools');

// Variáveis para configuração
let tessClient = null;

// Inicialização do servlet
function init(config) {
  // Inicializar cliente TESS com configuração
  tessClient = new TessClient(
    config.TESS_API_KEY || process.env.TESS_API_KEY || '',
    config.TESS_API_URL || process.env.TESS_API_URL || 'https://tess.pareto.io/api'
  );
  
  console.log('TESS Servlet inicializado com sucesso');
  return { success: true };
}

// Definir as ferramentas TESS
const tools = {
  // Ferramenta: tess.list_agents
  'tess.list_agents': {
    description: 'Lista os agentes disponíveis no TESS.',
    parameters: {
      page: {
        type: 'number',
        description: 'Número da página para paginação',
        default: 1
      },
      per_page: {
        type: 'number',
        description: 'Número de itens por página',
        default: 15
      },
      type: {
        type: 'string',
        description: 'Filtrar por tipo de agente',
        optional: true
      },
      q: {
        type: 'string',
        description: 'Termo de busca para filtrar agentes',
        optional: true
      }
    },
    handler: async (params) => {
      if (!tessClient) {
        return { error: 'Cliente TESS não inicializado' };
      }
      
      try {
        return await tessClient.listAgents(params);
      } catch (error) {
        return { error: error.message };
      }
    }
  },

  // Ferramenta: tess.get_agent
  'tess.get_agent': {
    description: 'Obtém detalhes de um agente específico no TESS.',
    parameters: {
      agent_id: {
        type: 'string',
        description: 'ID do agente'
      }
    },
    handler: async (params) => {
      if (!tessClient) {
        return { error: 'Cliente TESS não inicializado' };
      }
      
      try {
        return await tessClient.getAgent(params.agent_id);
      } catch (error) {
        return { error: error.message };
      }
    }
  },

  // Ferramenta: tess.execute_agent
  'tess.execute_agent': {
    description: 'Executa um agente específico no TESS.',
    parameters: {
      agent_id: {
        type: 'string',
        description: 'ID do agente a ser executado'
      },
      input_text: {
        type: 'string',
        description: 'Texto de entrada para o agente'
      },
      temperature: {
        type: 'string',
        description: 'Temperatura para geração (de 0 a 1)',
        default: '1',
        optional: true
      },
      model: {
        type: 'string',
        description: 'Modelo a ser usado',
        default: 'tess-ai-light',
        optional: true
      },
      file_ids: {
        type: 'array',
        description: 'IDs de arquivos a serem usados',
        optional: true
      },
      wait_execution: {
        type: 'boolean',
        description: 'Aguardar conclusão da execução',
        default: false,
        optional: true
      }
    },
    handler: async (params) => {
      if (!tessClient) {
        return { error: 'Cliente TESS não inicializado' };
      }
      
      try {
        const options = {
          temperature: params.temperature,
          model: params.model,
          fileIds: params.file_ids,
          waitExecution: params.wait_execution
        };
        return await tessClient.executeAgent(params.agent_id, params.input_text, options);
      } catch (error) {
        return { error: error.message };
      }
    }
  },

  // Ferramenta: tess.upload_file
  'tess.upload_file': {
    description: 'Faz upload de um arquivo para o TESS.',
    parameters: {
      file_path: {
        type: 'string',
        description: 'Caminho do arquivo a ser enviado'
      },
      process: {
        type: 'boolean',
        description: 'Se o arquivo deve ser processado após o upload',
        default: false,
        optional: true
      }
    },
    handler: async (params) => {
      if (!tessClient) {
        return { error: 'Cliente TESS não inicializado' };
      }
      
      try {
        return await tessClient.uploadFile(params.file_path, params.process);
      } catch (error) {
        return { error: error.message };
      }
    }
  }
};

// Função principal para lidar com chamadas MCP
async function handleMcpCall(request) {
  const { method, params } = request;
  
  // Rota para listar ferramentas
  if (method === 'tools/list') {
    return {
      tools: Object.entries(tools).map(([name, tool]) => ({
        name,
        description: tool.description,
        parameters: Object.entries(tool.parameters).map(([paramName, paramConfig]) => ({
          name: paramName,
          type: paramConfig.type,
          description: paramConfig.description,
          required: !paramConfig.optional,
          default: paramConfig.default
        }))
      }))
    };
  }
  
  // Rota para chamar uma ferramenta
  if (method === 'tools/call') {
    const { name, arguments: args } = params;
    const tool = tools[name];
    
    if (!tool) {
      return {
        content: [{
          type: 'text',
          text: `Ferramenta não encontrada: ${name}`
        }],
        isError: true
      };
    }
    
    try {
      const result = await tool.handler(args);
      
      // Verificar se o resultado é um erro
      if (result && result.error) {
        return {
          content: [{
            type: 'text',
            text: result.error
          }],
          isError: true
        };
      }
      
      // Formatar o resultado como conteúdo MCP
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }],
        isError: false
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: `Erro ao executar ferramenta: ${error.message}`
        }],
        isError: true
      };
    }
  }
  
  return {
    content: [{
      type: 'text',
      text: `Método desconhecido: ${method}`
    }],
    isError: true
  };
}

module.exports = {
  init,
  handleMcpCall,
  tools
}; 