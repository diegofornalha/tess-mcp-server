# Arquitetura de Plugins para Servidores MCP

## Visão Geral

Este documento descreve a nova arquitetura de plugins para servidores MCP implementada no projeto `crew_ai_tess_pareto`. Esta arquitetura foi projetada para resolver um dos problemas críticos identificados na análise de inconsistências do projeto: a multiplicidade de implementações de servidores MCP sem uma estrutura clara para gerenciá-las.

A solução adotada permite que múltiplas implementações de servidores MCP coexistam e sejam utilizadas de forma intercambiável, mantendo a consistência arquitetural e facilitando a adição de novas implementações no futuro.

## Componentes Principais

A arquitetura de plugins para servidores MCP é composta pelos seguintes componentes:

### 1. Interface Comum (MCPServerInterface)

Localizada em `domain/interfaces/mcp_server.py`, esta interface define o contrato que todas as implementações de servidor MCP devem seguir. Ela especifica métodos para:

- Controle do ciclo de vida (`start`, `stop`)
- Monitoramento (`get_status`, `health_check`)
- Funcionalidades básicas (`list_tools`, `execute_tool`)
- Metadados (`get_endpoint`, `get_server_info`)

Esta interface garante que todos os servidores MCP sejam intercambiáveis do ponto de vista do cliente.

### 2. Sistema de Registro (MCPServerRegistry)

Localizado em `infrastructure/mcp_servers/registry.py`, este componente implementa o padrão Registry para gerenciar diferentes implementações de servidores MCP. Ele permite:

- Registrar novas implementações com metadados
- Listar servidores disponíveis
- Obter uma implementação específica por ID
- Obter metadados de um servidor específico

### 3. Factory Pattern (MCPServerFactory)

Localizado em `application/factories/mcp_server_factory.py`, este componente implementa o padrão Factory Method para criar instâncias concretas de servidores MCP. Ele:

- Cria instâncias de servidores baseado em seu ID
- Encapsula a lógica de criação
- Fornece um ponto centralizado para obter instâncias de servidores

### 4. Adaptadores para Implementações Específicas

Cada implementação de servidor MCP é encapsulada em um adaptador que implementa a interface comum:

- `infrastructure/mcp_servers/fastapi_adapter.py`: Adaptador para o servidor FastAPI (Python)
- `infrastructure/mcp_servers/nodejs_wasm_adapter.py`: Adaptador para o servidor Node.js/WebAssembly

Estes adaptadores garantem que cada implementação possa ser usada de forma intercambiável, independentemente de suas diferenças internas.

## Como Funciona

### Registro de Servidores

Antes de usar qualquer servidor MCP, é necessário registrá-lo no sistema:

```python
from infrastructure.mcp_servers.registry import MCPServerRegistry
from infrastructure.mcp_servers.fastapi_adapter import FastAPIMCPServerAdapter

MCPServerRegistry.register(
    server_id="fastapi",
    server_class=FastAPIMCPServerAdapter,
    description="Servidor MCP implementado com FastAPI (Python)",
    language="Python",
    framework="FastAPI"
)
```

### Listagem de Servidores Disponíveis

Para listar os servidores disponíveis:

```python
from application.factories.mcp_server_factory import MCPServerFactory

available_servers = MCPServerFactory.list_available_servers()
for server_id, metadata in available_servers.items():
    print(f"Servidor: {server_id}")
    print(f"Descrição: {metadata.get('description')}")
    print(f"Linguagem: {metadata.get('language')}")
```

### Criação de Instâncias de Servidores

Para criar uma instância de um servidor específico:

```python
from application.factories.mcp_server_factory import MCPServerFactory

# Criar servidor FastAPI na porta 8080
server = MCPServerFactory.create("fastapi", port=8080)

# Iniciar o servidor
server.start()

# Usar o servidor
tools = server.list_tools()

# Parar o servidor
server.stop()
```

### Uso Intercambiável

Uma vez que todos os servidores implementam a mesma interface, eles podem ser usados de forma intercambiável:

```python
def process_with_any_server(server_id, tool_id, params):
    server = MCPServerFactory.create(server_id)
    server.start()
    
    try:
        result = server.execute_tool(tool_id, params)
        return result
    finally:
        server.stop()

# Usar com FastAPI
result1 = process_with_any_server("fastapi", "search_info", {"query": "exemplo"})

# Usar com Node.js/WebAssembly
result2 = process_with_any_server("nodejs-wasm", "search_info", {"query": "exemplo"})
```

## Como Adicionar Novas Implementações

Para adicionar uma nova implementação de servidor MCP:

1. **Crie um Adaptador**: Implemente um novo adaptador que siga a interface `MCPServerInterface`

```python
from domain.interfaces.mcp_server import MCPServerInterface

class MyNewMCPServerAdapter(MCPServerInterface):
    def __init__(self, host="localhost", port=9000):
        self.host = host
        self.port = port
        # Inicialização específica
        
    def start(self):
        # Implementação específica
        pass
    
    # Implementação dos demais métodos da interface
```

2. **Registre no Sistema**: Registre a nova implementação no sistema

```python
from infrastructure.mcp_servers.registry import MCPServerRegistry
from my_module import MyNewMCPServerAdapter

MCPServerRegistry.register(
    server_id="my-new-server",
    server_class=MyNewMCPServerAdapter,
    description="Minha nova implementação de servidor MCP",
    language="Python",
    framework="Custom"
)
```

3. **Use a Nova Implementação**: Use a nova implementação como qualquer outra

```python
from application.factories.mcp_server_factory import MCPServerFactory

server = MCPServerFactory.create("my-new-server")
server.start()
# Use o servidor
server.stop()
```

## Benefícios da Arquitetura de Plugins

Esta arquitetura proporciona diversos benefícios:

1. **Flexibilidade**: Suporte para múltiplas implementações com diferentes características e otimizações.
2. **Extensibilidade**: Facilidade para adicionar novas implementações sem modificar o código existente.
3. **Consistência**: Interface comum garantindo comportamento consistente para o cliente.
4. **Encapsulamento**: Detalhes de implementação específicos ficam isolados em seus adaptadores.
5. **Testabilidade**: Facilidade para substituir implementações reais por mocks em testes.
6. **Documentação Viva**: A interface serve como documentação clara do que um servidor MCP deve fazer.

## Exemplo Prático

Um exemplo completo de uso desta arquitetura pode ser encontrado em `examples/mcp/example_mcp_servers.py`, que demonstra:

- Registro de diferentes implementações
- Listagem de servidores disponíveis
- Criação de instâncias com diferentes configurações
- Uso das funcionalidades através da interface comum

## Conclusão

A arquitetura de plugins para servidores MCP resolve o problema da multiplicidade de implementações transformando-o em uma vantagem: agora o projeto pode se beneficiar de diferentes implementações para diferentes casos de uso, mantendo uma estrutura clara e consistente.

Esta arquitetura representa um passo importante na direção de um sistema mais modular, manutenível e extensível, alinhado com os princípios de Clean Architecture e SOLID. 