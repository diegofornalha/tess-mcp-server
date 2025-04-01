# TESS-MCP Server

Servidor MCP (Model Context Protocol) para integração com a API TESS, permitindo utilizar agentes TESS através do protocolo MCP.

## Sobre

O TESS-MCP Server cria uma ponte entre os agentes TESS e ferramentas que utilizam o protocolo MCP. Isso permite que qualquer cliente compatível com MCP (como Claude, ChatGPT ou outros LLMs) possa acessar e controlar agentes TESS.

## Recursos

- ✅ Listar agentes TESS disponíveis
- ✅ Obter detalhes de agentes específicos
- ✅ Executar agentes com texto e arquivos
- ✅ Fazer upload de arquivos para processamento
- ✅ Integração com Smithery para distribuição
- ✅ Modo YOLO para execução automática

## Pré-requisitos

- Node.js v18 ou superior
- Conta TESS com chave de API válida
- npm ou yarn

## Instalação

```bash
# Clonar o repositório
git clone https://github.com/diegofornalha/mcp-server-tess.git
cd mcp-server-tess

# Instalar dependências
npm install

# Executar script de configuração
npm run setup
```

## Configuração

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
# Chave de API TESS (obrigatória)
TESS_API_KEY=sua_chave_api_aqui

# URL da API TESS (opcional)
TESS_API_URL=https://tess.pareto.io/api

# Porta para o servidor MCP (opcional, padrão: 3001)
PORT=3001
```

## Uso

### Iniciar o servidor

```bash
# Modo normal
npm start

# Modo desenvolvimento (com reinício automático)
npm run dev

# Modo YOLO (execução automática sem confirmações)
npm run yolo
```

### Testando o servidor

Você pode testar o servidor com um simples comando curl:

```bash
# Verificar status do servidor
curl http://localhost:3001/health

# Listar ferramentas disponíveis
curl -X POST http://localhost:3001/tools/list

# Executar uma ferramenta (listar agentes TESS)
curl -X POST http://localhost:3001/tools/call \
  -H "Content-Type: application/json" \
  -d '{"name": "tess.list_agents", "arguments": {"page": 1, "per_page": 10}}'
```

## Integração com Smithery

Este servidor pode ser publicado como um pacote Smithery para fácil distribuição:

```bash
# Preparar para publicação
npm run smithery:build

# Publicar no registro Smithery
npm run smithery:publish
```

## Ferramentas disponíveis

O servidor expõe as seguintes ferramentas MCP:

### tess.list_agents

Lista os agentes disponíveis no TESS.

**Parâmetros:**
- `page` (number, opcional): Número da página para paginação (padrão: 1)
- `per_page` (number, opcional): Itens por página (padrão: 15)
- `type` (string, opcional): Filtro por tipo de agente
- `q` (string, opcional): Termo de busca para filtrar agentes

### tess.get_agent

Obtém detalhes de um agente específico no TESS.

**Parâmetros:**
- `agent_id` (string, obrigatório): ID do agente

### tess.execute_agent

Executa um agente específico no TESS.

**Parâmetros:**
- `agent_id` (string, obrigatório): ID do agente
- `input_text` (string, obrigatório): Texto de entrada para o agente
- `temperature` (string, opcional): Temperatura para geração (0 a 1, padrão: 1)
- `model` (string, opcional): Modelo a ser usado (padrão: tess-ai-light)
- `file_ids` (array, opcional): IDs de arquivos a serem usados
- `wait_execution` (boolean, opcional): Aguardar conclusão da execução (padrão: false)

### tess.upload_file

Faz upload de um arquivo para o TESS.

**Parâmetros:**
- `file_path` (string, obrigatório): Caminho do arquivo a ser enviado
- `process` (boolean, opcional): Se o arquivo deve ser processado após o upload (padrão: false)

## Modo YOLO

O "modo YOLO" (You Only Live Once) permite a execução automática de comandos sem necessidade de confirmações manuais. Isso é útil para ambientes de desenvolvimento e testes rápidos.

Para ativar o modo YOLO:

```bash
# Via npm
npm run yolo

# Via shell script
./scripts/yolo.sh
```

## Licença

MIT

## Contato

Para suporte ou dúvidas, entre em contato com a equipe TESS ou abra uma issue no GitHub.