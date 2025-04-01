# TESS-MCP Server

Servidor MCP para integração com a API TESS, permitindo utilizar agentes TESS através do protocolo MCP (Model Context Protocol).

## 📚 Sobre

TESS-MCP Server é um adaptador que permite utilizar os agentes TESS através do protocolo MCP, facilitando a integração com modelos de IA como GPT-4, Claude e outros que suportem o padrão MCP.


## 🚀 Características

- **Integração TESS-MCP**: Execução de agentes TESS via protocolo MCP
- **Ferramentas disponíveis**:
  - `tess.list_agents`: Lista os agentes disponíveis no TESS
  - `tess.get_agent`: Obtém detalhes de um agente específico
  - `tess.execute_agent`: Executa um agente TESS
  - `tess.upload_file`: Faz upload de um arquivo para o TESS
- **WebSocket**: Comunicação em tempo real para monitoramento de execuções
- **Cliente de exemplo**: Interface web para testar as ferramentas
- **Scripts utilitários**: Configuração, inicialização e demonstração

## 🔧 Instalação

### Pré-requisitos

- Node.js 18 ou superior
- NPM
- Chave de API TESS válida

### Configuração

1. Clone o repositório:
```bash
git clone https://github.com/diegofornalha/mcp-server-tess.git
cd mcp-server-tess
```

2. Execute o script de configuração:
```bash
./scripts/setup.sh
```

3. Configure sua API Key do TESS no arquivo `.env`:
```
TESS_API_KEY="sua_api_key_aqui"
```

## 🖥️ Uso

### Iniciar o servidor

```bash
# Modo desenvolvimento (com hot-reload)
./scripts/start.sh

# Modo produção
./scripts/start.sh --prod
```

### Testar a conexão

Acesse [http://localhost:3001](http://localhost:3001) em seu navegador para abrir o cliente de demonstração.

Ou verifique a saúde do servidor via terminal:
```bash
curl http://localhost:3001/health
```

### Demonstração de integração

Execute a demonstração de integração para ver como utilizar o TESS-MCP em uma aplicação:

```bash
./scripts/run-integration.sh
```

## 🧩 Integração com MCP

### Listar ferramentas

```js
const response = await fetch('http://localhost:3001/tools/list', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({})
});

const tools = await response.json();
console.log(tools);
```

### Chamar uma ferramenta

```js
const response = await fetch('http://localhost:3001/tools/call', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'tess.execute_agent',
    arguments: {
      agent_id: '123',
      input_text: 'Olá, TESS!'
    }
  })
});

const result = await response.json();
console.log(result);
```

## 📋 API MCP

O TESS-MCP Server expõe os seguintes endpoints MCP:

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/tools/list` | POST | Lista as ferramentas disponíveis |
| `/tools/call` | POST | Executa uma ferramenta |
| `/health` | GET | Verifica o status do servidor |

## 📘 Comparação com DesktopCommanderMCP

O TESS-MCP Server foi aprimorado com inspiração no DesktopCommanderMCP, aplicando as seguintes melhorias:

- **Estrutura organizada**: Separação clara de responsabilidades em módulos
- **Scripts confiáveis**: Scripts de configuração e inicialização inspirados no DesktopCommanderMCP
- **Documentação detalhada**: Instruções claras de instalação, uso e integração
- **Cliente de demonstração**: Interface web para testar a API
- **Exemplo de integração**: Código JavaScript demonstrando o uso em aplicações

## 📦 Publicação e Distribuição

### Publicar no GitHub

Para publicar este projeto no GitHub:

1. Crie um novo repositório em [GitHub](https://github.com/new)
2. Inicialize o Git e envie para o GitHub:

```bash
git init
git add .
git commit -m "Versão inicial do servidor TESS-MCP"
git branch -M main
git remote add origin https://github.com/seu-usuario/mcp-server-tess.git
git push -u origin main
```

### Publicar no Smithery

Este projeto está configurado para ser publicado na plataforma Smithery, permitindo que outros usuários utilizem o servidor TESS-MCP facilmente.

1. Gere o arquivo de configuração do Smithery:
```bash
npm run smithery:build
```

2. Faça login no Smithery CLI:
```bash
npx @smithery/cli@latest login
```

3. Publique o projeto:
```bash
npm run smithery:publish
```

4. Após a publicação, usuários poderão instalar o servidor com:
```bash
npx -y @smithery/cli@latest install @seu-usuario/mcp-server-tess --client claude --config '{"TESS_API_KEY":"sua_chave_api"}'
```

5. Para testar localmente antes de publicar:
```bash
npx @smithery/cli@latest run .
```

## 🔒 Segurança

- Proteja sua API Key do TESS
- Configure corretamente as origins CORS em ambiente de produção
- Limite o acesso ao servidor em ambientes de produção

## 📄 Licença

Este projeto é licenciado sob a [Licença MIT](LICENSE).

## 🙏 Agradecimentos

- [DesktopCommanderMCP](https://github.com/wonderwhy-er/DesktopCommanderMCP) por fornecer inspiração para a estrutura e scripts
- [TESS API](https://tess.pareto.io) por fornecer a plataforma de agentes AI
- [Model Context Protocol](https://modelcontextprotocol.github.io) por estabelecer o padrão de comunicação entre ferramentas e modelos 