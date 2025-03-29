# Cliente MCP Unificado

Este módulo fornece uma interface unificada para interação com diferentes tipos de servidores MCP (Model Context Protocol).

## Funcionalidades

- Suporte para múltiplos servidores MCP
- Abstração para comunicação com ferramentas via MCP
- Gerenciamento de sessões MCP
- Configuração flexível

## Uso

```python
from mcp_client import MCPClient

# Inicializar cliente MCP
client = MCPClient()

# Listar ferramentas disponíveis
tools = client.list_tools()

# Executar uma ferramenta
result = client.execute_tool("tool_id", {"param": "value"})
```

## Características

- **Interface única:** Uma classe para interagir com diferentes tipos de servidores MCP
- **Tipos de serviço suportados:**
  - `generic`: Cliente MCP genérico para testes e desenvolvimento local
  - `veyrax`: Cliente para interação com serviços Veyrax (memórias)
  - `mcp_run`: Cliente para automação de agentes via MCP.run

## Uso Básico

```python
from infrastructure.mcp_client import MCPClientUnificado

# Cliente genérico
cliente = MCPClientUnificado(service_type="generic")
success, tools = cliente.get_tools()
success, result = cliente.run_tool("echo", "say", {"message": "Teste"})

# Cliente Veyrax
cliente_veyrax = MCPClientUnificado(service_type="veyrax")
success, result = cliente_veyrax.save_memory("Teste de memória", "teste")
success, memories = cliente_veyrax.get_memories(limit=5)

# Cliente MCP.run
cliente_mcprun = MCPClientUnificado(service_type="mcp_run")
success, session = cliente_mcprun.start_session()
success, result = cliente_mcprun.run_tool("echo", "say", {"message": "Teste"})
```

## Métodos Comuns

- `get_tools()`: Lista ferramentas disponíveis
- `run_tool(tool_name, action, params)`: Executa uma ferramenta
- `validate_response(response)`: Valida resposta HTTP
- `make_request(endpoint, method, data)`: Faz requisição HTTP para o servidor

## Métodos Específicos

### Cliente Veyrax

- `save_memory(content, tool)`: Salva uma memória
- `get_memories(limit=10)`: Recupera memórias

### Cliente MCP.run

- `start_session()`: Inicia uma sessão
- `get_session_status(session_id)`: Verifica status de uma sessão

## Exemplo Completo

Veja o arquivo `example.py` para exemplos completos de uso.

## Configuração

Configure as URLs e chaves através das variáveis de ambiente:
- `VEYRAX_API_KEY`: Chave para serviço Veyrax
- `MCP_SERVER_URL`: URL do servidor MCP genérico
- `MCPRUN_SERVER_URL`: URL do servidor MCP.run 