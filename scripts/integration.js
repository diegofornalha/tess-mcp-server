/**
 * Script de demonstração de integração entre TESS-MCP e DesktopCommanderMCP
 * 
 * Este script mostra como conectar um cliente MCP ao servidor TESS-MCP
 * e utilizar as ferramentas TESS em uma aplicação JavaScript.
 */

// Importe os módulos necessários
const http = require('http');
const readline = require('readline');

// Configurações
const TESS_MCP_URL = process.env.TESS_MCP_URL || 'http://localhost:3001';

// Crie uma interface para leitura de input do usuário
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

/**
 * Função para fazer requisições HTTP para o servidor TESS-MCP
 * 
 * @param {string} endpoint - Endpoint a ser chamado
 * @param {object} data - Dados a serem enviados (para POST)
 * @returns {Promise<object>} - Resposta da requisição
 */
async function makeRequest(endpoint, data = null) {
  return new Promise((resolve, reject) => {
    // Configurações da requisição
    const options = {
      hostname: TESS_MCP_URL.replace(/^https?:\/\//, '').split(':')[0],
      port: TESS_MCP_URL.includes(':') ? TESS_MCP_URL.split(':')[2] : 80,
      path: endpoint,
      method: data ? 'POST' : 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    };
    
    // Cria a requisição
    const req = http.request(options, (res) => {
      let responseData = '';
      
      // Coleta dados da resposta
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      
      // Finaliza e resolve a Promise
      res.on('end', () => {
        try {
          const parsedData = JSON.parse(responseData);
          resolve(parsedData);
        } catch (e) {
          reject(new Error(`Erro ao processar resposta: ${e.message}`));
        }
      });
    });
    
    // Trata erros de requisição
    req.on('error', (error) => {
      reject(new Error(`Erro na requisição: ${error.message}`));
    });
    
    // Envia dados para requisições POST
    if (data) {
      req.write(JSON.stringify(data));
    }
    
    // Finaliza a requisição
    req.end();
  });
}

/**
 * Listar todas as ferramentas disponíveis no servidor TESS-MCP
 */
async function listTools() {
  try {
    console.log('\n📋 Listando ferramentas disponíveis...');
    const response = await makeRequest('/tools/list', {});
    
    if (response.tools && response.tools.length > 0) {
      console.log('\n✅ Ferramentas disponíveis:');
      response.tools.forEach((tool, index) => {
        console.log(`\n[${index + 1}] ${tool.name}`);
        console.log(`   ${tool.description}`);
        
        if (tool.parameters && tool.parameters.length > 0) {
          console.log('   Parâmetros:');
          tool.parameters.forEach(param => {
            const required = param.required ? 'obrigatório' : 'opcional';
            console.log(`    - ${param.name} (${param.type}, ${required}): ${param.description}`);
          });
        }
      });
    } else {
      console.log('❌ Nenhuma ferramenta disponível.');
    }
  } catch (error) {
    console.error(`❌ Erro ao listar ferramentas: ${error.message}`);
  }
}

/**
 * Executar um agente TESS
 * 
 * @param {string} agentId - ID do agente a ser executado
 * @param {string} inputText - Texto de entrada para o agente
 */
async function executeAgent(agentId, inputText) {
  try {
    console.log(`\n🚀 Executando agente ${agentId}...`);
    
    const request = {
      name: 'tess.execute_agent',
      arguments: {
        agent_id: agentId,
        input_text: inputText,
        wait_execution: true
      }
    };
    
    const response = await makeRequest('/tools/call', request);
    
    if (response.isError) {
      console.error(`❌ Erro ao executar agente: ${response.content[0].text}`);
    } else {
      console.log('\n✅ Execução concluída!');
      // Tente fazer o parse da resposta (que está em formato texto JSON)
      try {
        const result = JSON.parse(response.content[0].text);
        console.log('\nResultado:');
        
        if (result.output) {
          console.log('\n' + result.output);
        } else {
          console.log(JSON.stringify(result, null, 2));
        }
      } catch (e) {
        // Se falhar o parse, mostra o texto diretamente
        console.log(response.content[0].text);
      }
    }
  } catch (error) {
    console.error(`❌ Erro ao executar agente: ${error.message}`);
  }
}

/**
 * Obter detalhes de um agente específico
 * 
 * @param {string} agentId - ID do agente a ser consultado
 */
async function getAgentDetails(agentId) {
  try {
    console.log(`\n🔍 Obtendo detalhes do agente ${agentId}...`);
    
    const request = {
      name: 'tess.get_agent',
      arguments: {
        agent_id: agentId
      }
    };
    
    const response = await makeRequest('/tools/call', request);
    
    if (response.isError) {
      console.error(`❌ Erro ao obter detalhes: ${response.content[0].text}`);
    } else {
      console.log('\n✅ Detalhes do agente:');
      
      try {
        const agentDetails = JSON.parse(response.content[0].text);
        console.log(`\nNome: ${agentDetails.name}`);
        console.log(`Descrição: ${agentDetails.description || 'N/A'}`);
        console.log(`Tipo: ${agentDetails.type || 'N/A'}`);
        
        if (agentDetails.parameters && agentDetails.parameters.length > 0) {
          console.log('\nParâmetros:');
          agentDetails.parameters.forEach(param => {
            console.log(`- ${param.name}: ${param.description || 'N/A'}`);
          });
        }
      } catch (e) {
        // Se falhar o parse, mostra o texto diretamente
        console.log(response.content[0].text);
      }
    }
  } catch (error) {
    console.error(`❌ Erro ao obter detalhes do agente: ${error.message}`);
  }
}

/**
 * Menu principal
 */
async function showMenu() {
  console.log('\n========================================');
  console.log('🧩 Demo de Integração TESS-MCP');
  console.log('========================================');
  console.log('1. Listar ferramentas disponíveis');
  console.log('2. Executar um agente TESS');
  console.log('3. Obter detalhes de um agente');
  console.log('0. Sair');
  console.log('========================================');
  
  rl.question('Escolha uma opção: ', async (answer) => {
    switch (answer) {
      case '1':
        await listTools();
        setTimeout(showMenu, 1000);
        break;
        
      case '2':
        rl.question('\nID do agente: ', (agentId) => {
          rl.question('Texto de entrada: ', async (inputText) => {
            await executeAgent(agentId, inputText);
            setTimeout(showMenu, 1000);
          });
        });
        break;
        
      case '3':
        rl.question('\nID do agente: ', async (agentId) => {
          await getAgentDetails(agentId);
          setTimeout(showMenu, 1000);
        });
        break;
        
      case '0':
        console.log('\n👋 Até logo!');
        rl.close();
        break;
        
      default:
        console.log('\n❌ Opção inválida!');
        setTimeout(showMenu, 500);
    }
  });
}

/**
 * Verificar conexão com o servidor TESS-MCP
 */
async function checkConnection() {
  try {
    const response = await makeRequest('/health');
    
    if (response.status === 'ok') {
      console.log('✅ Conexão com servidor TESS-MCP estabelecida!');
      console.log(`📡 URL: ${TESS_MCP_URL}`);
      console.log(`🔄 Versão: ${response.version || 'N/A'}`);
      console.log(`🔌 WebSocket: ${response.websocket ? 'Disponível' : 'Indisponível'}`);
      
      // Inicia o menu após verificar conexão
      showMenu();
    } else {
      console.error('❌ Servidor TESS-MCP está online, mas reportou estado anormal.');
      process.exit(1);
    }
  } catch (error) {
    console.error(`❌ Erro ao conectar ao servidor TESS-MCP: ${error.message}`);
    console.log('\nVerifique se o servidor está rodando com:');
    console.log('./scripts/start.sh');
    process.exit(1);
  }
}

// Inicia o aplicativo verificando a conexão
console.log('🔄 Verificando conexão com o servidor TESS-MCP...');
checkConnection(); 