/**
 * Ferramentas TESS para MCP
 * 
 * Este módulo define as ferramentas TESS que serão expostas pelo servidor MCP.
 * Permite acessar a API TESS através do protocolo MCP.
 */

const axios = require('axios');
const fs = require('fs');
const path = require('path');
const FormData = require('form-data');

/**
 * Cliente para interação com a API do TESS
 */
class TessClient {
  /**
   * Cria uma nova instância do cliente TESS
   * 
   * @param {string} apiKey - Chave de API para autenticação com o TESS
   * @param {string} apiUrl - URL base da API TESS (padrão: https://tess.pareto.io/api)
   */
  constructor(apiKey, apiUrl = 'https://tess.pareto.io/api') {
    if (!apiKey) {
      throw new Error('TESS API Key é obrigatória');
    }
    
    this.apiKey = apiKey;
    this.apiUrl = apiUrl;
    
    // Cliente HTTP com cabeçalhos de autenticação
    this.client = axios.create({
      baseURL: apiUrl,
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
  }
  
  /**
   * Lista os agentes disponíveis no TESS
   * 
   * @param {Object} options - Opções de filtragem e paginação
   * @param {number} [options.page=1] - Número da página
   * @param {number} [options.per_page=15] - Itens por página
   * @param {string} [options.type] - Filtro por tipo de agente
   * @param {string} [options.q] - Termo de busca
   * @returns {Promise<Object>} - Resultado da listagem de agentes
   */
  async listAgents(options = {}) {
    try {
      const params = {
        page: options.page || 1,
        per_page: options.per_page || 15
      };
      
      if (options.type) params.type = options.type;
      if (options.q) params.q = options.q;
      
      const response = await this.client.get('/agents', { params });
      return response.data;
    } catch (error) {
      this._handleError(error, 'Erro ao listar agentes');
    }
  }
  
  /**
   * Obtém detalhes de um agente específico
   * 
   * @param {string} agentId - ID do agente a ser consultado
   * @returns {Promise<Object>} - Detalhes do agente
   */
  async getAgent(agentId) {
    if (!agentId) {
      throw new Error('ID do agente é obrigatório');
    }
    
    try {
      const response = await this.client.get(`/agents/${agentId}`);
      return response.data;
    } catch (error) {
      this._handleError(error, `Erro ao obter agente ${agentId}`);
    }
  }
  
  /**
   * Executa um agente específico
   * 
   * @param {string} agentId - ID do agente a ser executado
   * @param {string} inputText - Texto de entrada para o agente
   * @param {Object} options - Opções adicionais
   * @param {string} [options.temperature='1'] - Temperatura para geração (0 a 1)
   * @param {string} [options.model='tess-ai-light'] - Modelo a ser usado
   * @param {Array} [options.fileIds] - IDs de arquivos a serem usados
   * @param {boolean} [options.waitExecution=false] - Aguardar conclusão da execução
   * @returns {Promise<Object>} - Resultado da execução
   */
  async executeAgent(agentId, inputText, options = {}) {
    if (!agentId) {
      throw new Error('ID do agente é obrigatório');
    }
    
    if (!inputText && !options.fileIds?.length) {
      throw new Error('Texto de entrada ou arquivos são obrigatórios');
    }
    
    try {
      const payload = {
        input: inputText,
        temperature: options.temperature || '1',
        model: options.model || 'tess-ai-light'
      };
      
      if (options.fileIds && options.fileIds.length > 0) {
        payload.file_ids = options.fileIds;
      }
      
      const response = await this.client.post(`/agents/${agentId}/execute`, payload);
      
      // Se waitExecution for true, aguarda a conclusão da execução
      if (options.waitExecution && response.data.id) {
        return await this._waitForExecution(response.data.id);
      }
      
      return response.data;
    } catch (error) {
      this._handleError(error, `Erro ao executar agente ${agentId}`);
    }
  }
  
  /**
   * Obtém o status atual de uma execução
   * 
   * @param {string} executionId - ID da execução a ser consultada
   * @returns {Promise<Object>} - Status atual da execução
   */
  async getExecutionStatus(executionId) {
    if (!executionId) {
      throw new Error('ID da execução é obrigatório');
    }
    
    try {
      const response = await this.client.get(`/executions/${executionId}`);
      return response.data;
    } catch (error) {
      this._handleError(error, `Erro ao obter status da execução ${executionId}`);
    }
  }
  
  /**
   * Faz upload de um arquivo para o TESS
   * 
   * @param {string} filePath - Caminho do arquivo a ser enviado
   * @param {boolean} [process=false] - Se o arquivo deve ser processado após o upload
   * @returns {Promise<Object>} - Resultado do upload
   */
  async uploadFile(filePath, process = false) {
    if (!filePath) {
      throw new Error('Caminho do arquivo é obrigatório');
    }
    
    if (!fs.existsSync(filePath)) {
      throw new Error(`Arquivo não encontrado: ${filePath}`);
    }
    
    try {
      const formData = new FormData();
      formData.append('file', fs.createReadStream(filePath));
      formData.append('process', process ? 'true' : 'false');
      
      const response = await axios.post(`${this.apiUrl}/files`, formData, {
        headers: {
          ...formData.getHeaders(),
          'Authorization': `Bearer ${this.apiKey}`,
        }
      });
      
      return response.data;
    } catch (error) {
      this._handleError(error, `Erro ao fazer upload do arquivo ${filePath}`);
    }
  }
  
  /**
   * Aguarda a conclusão da execução de um agente
   * 
   * @private
   * @param {string} executionId - ID da execução
   * @param {number} [maxRetries=60] - Número máximo de tentativas
   * @param {number} [interval=1000] - Intervalo entre tentativas (ms)
   * @returns {Promise<Object>} - Resultado final da execução
   */
  async _waitForExecution(executionId, maxRetries = 60, interval = 1000) {
    let retries = 0;
    
    while (retries < maxRetries) {
      try {
        const status = await this.getExecutionStatus(executionId);
        
        if (['completed', 'failed', 'error'].includes(status.status)) {
          return status;
        }
        
        await new Promise(resolve => setTimeout(resolve, interval));
        retries++;
      } catch (error) {
        this._handleError(error, `Erro ao verificar execução ${executionId}`);
      }
    }
    
    throw new Error(`Tempo esgotado aguardando execução ${executionId}`);
  }
  
  /**
   * Manipula erros da API
   * 
   * @private
   * @param {Error} error - Objeto de erro
   * @param {string} defaultMessage - Mensagem padrão
   */
  _handleError(error, defaultMessage) {
    if (error.response) {
      // Erro da API com resposta
      const status = error.response.status;
      const data = error.response.data;
      
      if (data.error || data.message) {
        throw new Error(`${defaultMessage}: ${data.error || data.message}`);
      } else if (status === 401) {
        throw new Error('Autenticação inválida. Verifique sua API Key.');
      } else if (status === 403) {
        throw new Error('Acesso negado. Permissões insuficientes.');
      } else if (status === 404) {
        throw new Error('Recurso não encontrado.');
      } else {
        throw new Error(`${defaultMessage}: Erro ${status}`);
      }
    } else if (error.request) {
      // Sem resposta da API
      throw new Error(`${defaultMessage}: Sem resposta do servidor`);
    } else {
      // Erro na configuração da requisição
      throw error;
    }
  }
}

// Definir ferramentas TESS para MCP
function createTessTools(tessClient) {
  return {
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
        return await tessClient.listAgents(params);
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
        return await tessClient.getAgent(params.agent_id);
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
        const options = {
          temperature: params.temperature,
          model: params.model,
          fileIds: params.file_ids,
          waitExecution: params.wait_execution
        };
        return await tessClient.executeAgent(params.agent_id, params.input_text, options);
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
        return await tessClient.uploadFile(params.file_path, params.process);
      }
    }
  };
}

module.exports = {
  TessClient,
  createTessTools
}; 