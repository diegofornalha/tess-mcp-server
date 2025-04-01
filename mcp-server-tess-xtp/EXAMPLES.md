# Exemplos de Integração com TESS-MCP Server

Este documento contém exemplos práticos de integração com o servidor TESS-MCP em diferentes linguagens e frameworks.

## Exemplo em JavaScript (Node.js)

### Configuração Básica

```javascript
const axios = require('axios');

const TESS_MCP_URL = 'http://localhost:3001';

async function callTessMcp(toolName, toolArguments) {
  try {
    const response = await axios.post(`${TESS_MCP_URL}/tools/call`, {
      name: toolName,
      arguments: toolArguments
    });
    
    return response.data;
  } catch (error) {
    console.error(`Erro ao chamar ferramenta ${toolName}:`, error.message);
    throw error;
  }
}

async function listTools() {
  try {
    const response = await axios.post(`${TESS_MCP_URL}/tools/list`, {});
    return response.data.tools;
  } catch (error) {
    console.error('Erro ao listar ferramentas:', error.message);
    throw error;
  }
}
```

### Listar Agentes TESS

```javascript
async function listTessAgents() {
  try {
    const result = await callTessMcp('tess.list_agents', {
      page: 1,
      per_page: 10
    });
    
    console.log('Agentes TESS disponíveis:');
    const agents = JSON.parse(result.content[0].text);
    
    agents.data.forEach(agent => {
      console.log(`- ${agent.name} (ID: ${agent.id}): ${agent.description || 'Sem descrição'}`);
    });
    
    return agents;
  } catch (error) {
    console.error('Erro ao listar agentes TESS:', error.message);
  }
}
```

### Executar um Agente TESS

```javascript
async function executeAgent(agentId, inputText) {
  try {
    console.log(`Executando agente ${agentId}...`);
    
    const result = await callTessMcp('tess.execute_agent', {
      agent_id: agentId,
      input_text: inputText,
      wait_execution: true
    });
    
    console.log('Resultado da execução:');
    const executionResult = JSON.parse(result.content[0].text);
    
    if (executionResult.output) {
      console.log(executionResult.output);
    } else {
      console.log(JSON.stringify(executionResult, null, 2));
    }
    
    return executionResult;
  } catch (error) {
    console.error('Erro ao executar agente:', error.message);
  }
}
```

### Exemplo Completo

```javascript
// Função principal
async function main() {
  try {
    const tools = await listTools();
    console.log('Ferramentas disponíveis:', tools.map(t => t.name).join(', '));
    
    const agents = await listTessAgents();
    
    if (agents && agents.data && agents.data.length > 0) {
      const firstAgent = agents.data[0];
      console.log(`\nExecutando o primeiro agente (${firstAgent.name})...`);
      
      await executeAgent(firstAgent.id, 'Olá! Pode me ajudar a entender como funciona o TESS?');
    } else {
      console.log('Nenhum agente TESS disponível.');
    }
  } catch (error) {
    console.error('Erro ao executar aplicação:', error.message);
  }
}

// Executar
main();
```

## Exemplo em Python

```python
import requests
import json

TESS_MCP_URL = 'http://localhost:3001'

def call_tess_mcp(tool_name, tool_arguments):
    """
    Chama uma ferramenta no servidor TESS-MCP
    
    Args:
        tool_name (str): Nome da ferramenta a ser chamada
        tool_arguments (dict): Argumentos para a ferramenta
        
    Returns:
        dict: Resultado da chamada da ferramenta
    """
    try:
        response = requests.post(
            f"{TESS_MCP_URL}/tools/call",
            json={
                "name": tool_name,
                "arguments": tool_arguments
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao chamar ferramenta {tool_name}: {str(e)}")
        raise

def list_tess_agents():
    """
    Lista os agentes disponíveis no TESS
    
    Returns:
        list: Lista de agentes TESS
    """
    try:
        result = call_tess_mcp("tess.list_agents", {
            "page": 1,
            "per_page": 10
        })
        
        # Extrair o texto JSON da resposta
        agents_data = json.loads(result["content"][0]["text"])
        
        print("Agentes TESS disponíveis:")
        for agent in agents_data["data"]:
            print(f"- {agent['name']} (ID: {agent['id']}): {agent.get('description', 'Sem descrição')}")
            
        return agents_data
    except Exception as e:
        print(f"Erro ao listar agentes TESS: {str(e)}")
        return None

def execute_agent(agent_id, input_text):
    """
    Executa um agente TESS
    
    Args:
        agent_id (str): ID do agente a ser executado
        input_text (str): Texto de entrada para o agente
        
    Returns:
        dict: Resultado da execução
    """
    try:
        print(f"Executando agente {agent_id}...")
        
        result = call_tess_mcp("tess.execute_agent", {
            "agent_id": agent_id,
            "input_text": input_text,
            "wait_execution": True
        })
        
        # Extrair o texto JSON da resposta
        execution_result = json.loads(result["content"][0]["text"])
        
        print("Resultado da execução:")
        if "output" in execution_result:
            print(execution_result["output"])
        else:
            print(json.dumps(execution_result, indent=2))
            
        return execution_result
    except Exception as e:
        print(f"Erro ao executar agente: {str(e)}")
        return None

def main():
    """Função principal do exemplo"""
    try:
        # Listar agentes
        agents = list_tess_agents()
        
        if agents and "data" in agents and len(agents["data"]) > 0:
            first_agent = agents["data"][0]
            print(f"\nExecutando o primeiro agente ({first_agent['name']})...")
            
            execute_agent(
                first_agent["id"], 
                "Olá! Pode me ajudar a entender como funciona o TESS?"
            )
        else:
            print("Nenhum agente TESS disponível.")
    except Exception as e:
        print(f"Erro ao executar aplicação: {str(e)}")

if __name__ == "__main__":
    main()
```

## Exemplo com WebSocket (Cliente JavaScript)

```javascript
const io = require('socket.io-client');

// Conectar ao servidor WebSocket
const socket = io('http://localhost:3001');

// Evento de conexão
socket.on('connect', () => {
  console.log('Conectado ao servidor TESS-MCP via WebSocket');
  
  // Listar ferramentas disponíveis
  socket.emit('list_tools');
});

// Receber lista de ferramentas
socket.on('tools_list', (data) => {
  console.log('Ferramentas disponíveis:');
  data.tools.forEach(tool => {
    console.log(`- ${tool.name}: ${tool.description}`);
  });
  
  // Após receber as ferramentas, executar um agente
  const agentId = 'seu-id-do-agente-aqui';
  executeAgent(agentId, 'Olá, como posso te ajudar hoje?');
});

// Função para executar um agente
function executeAgent(agentId, inputText) {
  console.log(`Executando agente ${agentId}...`);
  
  socket.emit('call_tool', {
    name: 'tess.execute_agent',
    arguments: {
      agent_id: agentId,
      input_text: inputText,
      wait_execution: false // Usar false para receber atualizações via WebSocket
    }
  });
}

// Receber resultado de uma ferramenta
socket.on('tool_result', (data) => {
  if (data.isError) {
    console.error(`Erro: ${data.error}`);
  } else {
    console.log('Execução iniciada:', data.result);
  }
});

// Receber atualizações da execução
socket.on('execution_update', (data) => {
  console.log(`Atualização da execução (${data.id}): Status = ${data.status}`);
});

// Receber conclusão da execução
socket.on('execution_complete', (data) => {
  console.log('Execução concluída:');
  console.log(data.data);
  
  // Fechar conexão após conclusão
  socket.disconnect();
});

// Receber erros
socket.on('error', (data) => {
  console.error(`Erro: ${data.message}`);
});

// Evento de desconexão
socket.on('disconnect', () => {
  console.log('Desconectado do servidor TESS-MCP');
});
```

## Integração com Frameworks

### Exemplo com Express.js

```javascript
const express = require('express');
const axios = require('axios');
const app = express();
const port = 3000;

app.use(express.json());
app.use(express.static('public'));

const TESS_MCP_URL = 'http://localhost:3001';

// Rota para listar agentes
app.get('/agents', async (req, res) => {
  try {
    const response = await axios.post(`${TESS_MCP_URL}/tools/call`, {
      name: 'tess.list_agents',
      arguments: {
        page: req.query.page || 1,
        per_page: req.query.per_page || 10
      }
    });
    
    const result = JSON.parse(response.data.content[0].text);
    res.json(result);
  } catch (error) {
    console.error('Erro ao listar agentes:', error.message);
    res.status(500).json({ error: 'Erro ao listar agentes TESS' });
  }
});

// Rota para executar um agente
app.post('/agents/:id/execute', async (req, res) => {
  try {
    const response = await axios.post(`${TESS_MCP_URL}/tools/call`, {
      name: 'tess.execute_agent',
      arguments: {
        agent_id: req.params.id,
        input_text: req.body.input,
        wait_execution: true
      }
    });
    
    const result = JSON.parse(response.data.content[0].text);
    res.json(result);
  } catch (error) {
    console.error('Erro ao executar agente:', error.message);
    res.status(500).json({ error: 'Erro ao executar agente TESS' });
  }
});

app.listen(port, () => {
  console.log(`Servidor de exemplo rodando em http://localhost:${port}`);
});
```