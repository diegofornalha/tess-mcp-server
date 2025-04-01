#!/usr/bin/env node

/**
 * Adaptador MCP para TESS
 * 
 * Este script cria um servidor HTTP que implementa o protocolo MCP
 * para expor as funcionalidades do TESS como ferramentas MCP.
 * Também inclui suporte a websockets para comunicação em tempo real.
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const http = require('http');
const { Server } = require('socket.io');
const { TessClient } = require('./src/tess_tools');

// Configurações
const PORT = process.env.PORT || 3001;
const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: '*', // Em produção, ajuste isso para as origens permitidas
    methods: ['GET', 'POST']
  }
});

// Middlewares
app.use(cors());
app.use(express.json());

// Inicializar cliente TESS
const tessClient = new TessClient(
  process.env.TESS_API_KEY,
  process.env.TESS_API_URL || 'https://tess.pareto.io/api'
);

// Definição das ferramentas TESS
const tessTools = {
  // Ferramenta: tess.list_agents
  'tess.list_agents': {
    name: 'tess.list_agents',
    description: 'Lista os agentes disponíveis no TESS.',
    parameters: [
      {
        name: 'page',
        type: 'number',
        description: 'Número da página para paginação',
        default: 1,
        required: false
      },
      {
        name: 'per_page',
        type: 'number',
        description: 'Número de itens por página',
        default: 15,
        required: false
      },
      {
        name: 'type',
        type: 'string',
        description: 'Filtrar por tipo de agente',
        required: false
      },
      {
        name: 'q',
        type: 'string',
        description: 'Termo de busca para filtrar agentes',
        required: false
      }
    ],
    handler: async (params) => {
      try {
        return await tessClient.listAgents(params);
      } catch (error) {
        console.error('Erro ao listar agentes:', error.message);
        throw new Error(error.message);
      }
    }
  },

  // Ferramenta: tess.get_agent
  'tess.get_agent': {
    name: 'tess.get_agent',
    description: 'Obtém detalhes de um agente específico no TESS.',
    parameters: [
      {
        name: 'agent_id',
        type: 'string',
        description: 'ID do agente',
        required: true
      }
    ],
    handler: async (params) => {
      try {
        return await tessClient.getAgent(params.agent_id);
      } catch (error) {
        console.error('Erro ao obter agente:', error.message);
        throw new Error(error.message);
      }
    }
  },

  // Ferramenta: tess.execute_agent
  'tess.execute_agent': {
    name: 'tess.execute_agent',
    description: 'Executa um agente específico no TESS.',
    parameters: [
      {
        name: 'agent_id',
        type: 'string',
        description: 'ID do agente a ser executado',
        required: true
      },
      {
        name: 'input_text',
        type: 'string',
        description: 'Texto de entrada para o agente',
        required: true
      },
      {
        name: 'temperature',
        type: 'string',
        description: 'Temperatura para geração (de 0 a 1)',
        default: '1',
        required: false
      },
      {
        name: 'model',
        type: 'string',
        description: 'Modelo a ser usado',
        default: 'tess-ai-light',
        required: false
      },
      {
        name: 'file_ids',
        type: 'array',
        description: 'IDs de arquivos a serem usados',
        required: false
      },
      {
        name: 'wait_execution',
        type: 'boolean',
        description: 'Aguardar conclusão da execução',
        default: false,
        required: false
      }
    ],
    handler: async (params, socket = null) => {
      try {
        const options = {
          temperature: params.temperature,
          model: params.model,
          fileIds: params.file_ids,
          waitExecution: params.wait_execution
        };
        
        // Se temos um socket e não estamos aguardando a execução, monitorar o progresso
        if (socket && !params.wait_execution) {
          const executionResult = await tessClient.executeAgent(
            params.agent_id, 
            params.input_text, 
            { ...options, waitExecution: false }
          );
          
          if (executionResult && executionResult.id) {
            // Iniciar polling da execução e enviar atualizações
            monitorExecution(executionResult.id, socket);
          }
          
          return executionResult;
        } else {
          // Execução normal
          return await tessClient.executeAgent(
            params.agent_id, 
            params.input_text, 
            options
          );
        }
      } catch (error) {
        console.error('Erro ao executar agente:', error.message);
        throw new Error(error.message);
      }
    }
  },

  // Ferramenta: tess.upload_file
  'tess.upload_file': {
    name: 'tess.upload_file',
    description: 'Faz upload de um arquivo para o TESS.',
    parameters: [
      {
        name: 'file_path',
        type: 'string',
        description: 'Caminho do arquivo a ser enviado',
        required: true
      },
      {
        name: 'process',
        type: 'boolean',
        description: 'Se o arquivo deve ser processado após o upload',
        default: false,
        required: false
      }
    ],
    handler: async (params) => {
      try {
        return await tessClient.uploadFile(params.file_path, params.process);
      } catch (error) {
        console.error('Erro ao fazer upload de arquivo:', error.message);
        throw new Error(error.message);
      }
    }
  }
};

/**
 * Monitora o progresso de uma execução e envia atualizações via websocket
 * 
 * @param {string} executionId - ID da execução a ser monitorada
 * @param {object} socket - Conexão websocket para enviar atualizações
 */
async function monitorExecution(executionId, socket) {
  const POLLING_INTERVAL = 1000; // 1 segundo
  const MAX_ATTEMPTS = 60; // 1 minuto
  let attempts = 0;
  
  const pollInterval = setInterval(async () => {
    try {
      const execStatus = await tessClient.getExecutionStatus(executionId);
      
      // Enviar atualização para o cliente
      socket.emit('execution_update', {
        id: executionId,
        status: execStatus.status,
        data: execStatus
      });
      
      // Se concluído ou falhou, parar polling
      if (['completed', 'failed', 'error'].includes(execStatus.status) || attempts >= MAX_ATTEMPTS) {
        clearInterval(pollInterval);
        
        // Enviar evento de conclusão
        socket.emit('execution_complete', {
          id: executionId,
          status: execStatus.status,
          data: execStatus
        });
      }
      
      attempts++;
    } catch (error) {
      console.error(`Erro ao monitorar execução ${executionId}:`, error);
      clearInterval(pollInterval);
      
      // Enviar evento de erro
      socket.emit('execution_error', {
        id: executionId,
        error: error.message
      });
    }
  }, POLLING_INTERVAL);
}

// Rota MCP - Listar ferramentas
app.post('/tools/list', (req, res) => {
  try {
    const tools = Object.values(tessTools).map(tool => ({
      name: tool.name,
      description: tool.description,
      parameters: tool.parameters
    }));
    
    res.json({ tools });
  } catch (error) {
    console.error('Erro ao listar ferramentas:', error);
    res.status(500).json({ error: error.message });
  }
});

// Rota MCP - Chamar ferramenta
app.post('/tools/call', async (req, res) => {
  try {
    const { name, arguments: args } = req.body;
    const tool = tessTools[name];
    
    if (!tool) {
      return res.status(404).json({ 
        content: [{ 
          type: 'text', 
          text: `Ferramenta não encontrada: ${name}` 
        }],
        isError: true 
      });
    }
    
    try {
      const result = await tool.handler(args);
      
      res.json({
        content: [{ 
          type: 'text', 
          text: JSON.stringify(result, null, 2) 
        }],
        isError: false
      });
    } catch (error) {
      res.status(500).json({
        content: [{ 
          type: 'text', 
          text: `Erro ao executar ferramenta: ${error.message}` 
        }],
        isError: true
      });
    }
  } catch (error) {
    console.error('Erro na chamada de ferramenta:', error);
    res.status(500).json({
      content: [{ 
        type: 'text', 
        text: `Erro interno do servidor: ${error.message}` 
      }],
      isError: true
    });
  }
});

// Rota de saúde
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    message: 'Servidor TESS-MCP em execução',
    websocket: true,
    version: '1.1.0'
  });
});

// Cliente de exemplo para demonstrar websocket
app.get('/', (req, res) => {
  res.sendFile(__dirname + '/public/index.html');
});

// Configuração do WebSocket
io.on('connection', (socket) => {
  console.log(`Cliente WebSocket conectado: ${socket.id}`);
  
  // Evento para listar ferramentas
  socket.on('list_tools', async () => {
    try {
      const tools = Object.values(tessTools).map(tool => ({
        name: tool.name,
        description: tool.description,
        parameters: tool.parameters
      }));
      
      socket.emit('tools_list', { tools });
    } catch (error) {
      socket.emit('error', { message: error.message });
    }
  });
  
  // Evento para executar uma ferramenta
  socket.on('call_tool', async (data) => {
    try {
      const { name, arguments: args } = data;
      const tool = tessTools[name];
      
      if (!tool) {
        return socket.emit('tool_result', { 
          error: `Ferramenta não encontrada: ${name}`,
          isError: true 
        });
      }
      
      try {
        // Passar o socket apenas para execute_agent para monitoramento
        const result = name === 'tess.execute_agent' 
          ? await tool.handler(args, socket)
          : await tool.handler(args);
        
        socket.emit('tool_result', {
          name,
          result,
          isError: false
        });
      } catch (error) {
        socket.emit('tool_result', {
          name,
          error: error.message,
          isError: true
        });
      }
    } catch (error) {
      socket.emit('error', { message: error.message });
    }
  });
  
  // Evento de desconexão
  socket.on('disconnect', () => {
    console.log(`Cliente WebSocket desconectado: ${socket.id}`);
  });
});

// Iniciar o servidor
server.listen(PORT, () => {
  console.log(`🚀 Servidor TESS-MCP rodando na porta ${PORT}`);
  console.log('');
  console.log('📝 Ferramentas disponíveis:');
  Object.keys(tessTools).forEach(toolName => {
    console.log(`- ${toolName}`);
  });
  console.log('');
  console.log('🔗 Para conectar clientes MCP, use:');
  console.log(`   - POST http://localhost:${PORT}/tools/list`);
  console.log(`   - POST http://localhost:${PORT}/tools/call`);
  console.log('');
  console.log('🔌 WebSocket disponível em:');
  console.log(`   - ws://localhost:${PORT}`);
  console.log('');
  console.log('🔄 Hot Reload ativado. Edite os arquivos e o servidor reiniciará automaticamente.');
}); 