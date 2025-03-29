# Servidor TESS-MCP

Este projeto implementa um servidor que expõe as funcionalidades da API TESS como ferramentas MCP (Model Context Protocol), permitindo que qualquer cliente MCP acesse os recursos do TESS.

## Arquitetura

O sistema usa o protocolo MCP para padronizar a comunicação entre clientes de IA e serviços, como o TESS. Com este adaptador, qualquer cliente MCP pode acessar as funcionalidades do TESS através de uma interface padrão.

```
┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│  Cliente MCP  │────▶│ Servidor MCP  │────▶│  API TESS   │
└──────────────┘     └───────────────┘     └──────────────┘
                          ▲
                          │
                     ┌────────────┐
                     │ TESS Tools │
                     └────────────┘
```

## Modos de Uso

O projeto oferece múltiplas formas de interação com o servidor TESS-MCP:

### 1. API MCP Direta

Acesse as ferramentas TESS diretamente através da API MCP usando qualquer cliente HTTP.

### 2. Interface Streamlit

Use a interface web Streamlit para interagir com as ferramentas TESS de forma visual e intuitiva.

### 3. Integração com CrewAI (Novo!)

Utilize uma equipe de agentes inteligentes para orquestrar o uso das ferramentas TESS através do framework CrewAI.

```
┌──────────────┐     ┌───────────────┐     ┌───────────────┐     ┌──────────────┐
│  Streamlit   │────▶│    CrewAI     │────▶│ Servidor MCP  │────▶│  API TESS   │
└──────────────┘     └───────────────┘     └───────────────┘     └──────────────┘
                          ▲
                          │
                     ┌────────────┐
                     │   Agentes  │
                     └────────────┘
```

## Requisitos

- Node.js 16.x ou superior
- Python 3.8 ou superior (para Streamlit e CrewAI)
- Conta TESS com chave de API válida

## Configuração

1. Clone este repositório
2. Instale as dependências:

```bash
npm install
```

3. Crie um arquivo `.env` baseado no `.env.example`:

```bash
cp .env.example .env
```

4. Edite o arquivo `.env` e adicione sua chave API TESS:

```
TESS_API_KEY=sua_chave_api_tess_aqui
```

## Uso

### Iniciando o servidor

Para iniciar o servidor MCP:

```bash
npm start
```

O servidor estará disponível na porta especificada (padrão: 3001).

### Desenvolvimento

Para execução com reload automático durante desenvolvimento:

```bash
npm run dev
```

### Usando a Integração CrewAI

A integração com CrewAI permite utilizar agentes inteligentes para orquestrar o uso das ferramentas TESS:

```bash
cd crew-integration
./setup.sh
```

Consulte o [README da integração CrewAI](./crew-integration/README.md) para mais detalhes.

## Ferramentas TESS disponíveis via MCP

O servidor expõe as seguintes ferramentas MCP:

### 📋 tess.list_agents

Lista os agentes disponíveis no TESS.

**Parâmetros:**
- `page` (número, opcional): Página para paginação (padrão: 1)
- `per_page` (número, opcional): Itens por página (padrão: 15)
- `type` (string, opcional): Filtrar por tipo de agente
- `q` (string, opcional): Termo de busca

**Exemplo:**
```json
{
  "name": "tess.list_agents",
  "arguments": {
    "page": 1,
    "per_page": 10,
    "type": "chat"
  }
}
```

### 🔍 tess.get_agent

Obtém detalhes de um agente específico no TESS.

**Parâmetros:**
- `agent_id` (string, obrigatório): ID do agente

**Exemplo:**
```json
{
  "name": "tess.get_agent",
  "arguments": {
    "agent_id": "abc123"
  }
}
```

### ▶️ tess.execute_agent

Executa um agente específico no TESS.

**Parâmetros:**
- `agent_id` (string, obrigatório): ID do agente a ser executado
- `input_text` (string, obrigatório): Texto de entrada para o agente
- `temperature` (string, opcional): Temperatura para geração (de 0 a 1) (padrão: "1")
- `model` (string, opcional): Modelo a ser usado (padrão: "tess-ai-light")
- `file_ids` (array, opcional): IDs de arquivos a serem usados
- `wait_execution` (boolean, opcional): Aguardar conclusão da execução (padrão: false)

**Exemplo:**
```json
{
  "name": "tess.execute_agent",
  "arguments": {
    "agent_id": "abc123",
    "input_text": "Como posso ajudá-lo hoje?",
    "temperature": "0.7",
    "wait_execution": true
  }
}
```

### 📤 tess.upload_file

Faz upload de um arquivo para o TESS.

**Parâmetros:**
- `file_path` (string, obrigatório): Caminho do arquivo a ser enviado
- `process` (boolean, opcional): Se o arquivo deve ser processado após o upload (padrão: false)

**Exemplo:**
```json
{
  "name": "tess.upload_file",
  "arguments": {
    "file_path": "/caminho/para/arquivo.pdf",
    "process": true
  }
}
```

## Integração com Clientes MCP

Este servidor pode ser acessado por qualquer cliente que implemente o protocolo MCP. Para interagir com o servidor:

1. **Listar Ferramentas Disponíveis**
   ```
   POST http://localhost:3000/tools/list
   ```

2. **Executar uma Ferramenta**
   ```
   POST http://localhost:3000/tools/call
   Content-Type: application/json
   
   {
     "name": "tess.list_agents",
     "arguments": {}
   }
   ```

## Considerações de Segurança

- Use HTTPS em produção
- Não compartilhe sua chave API TESS
- Considere implementar autenticação para o servidor MCP em ambientes de produção

## Solução de Problemas

- Se encontrar erros de autenticação, verifique se sua chave API TESS é válida
- Para problemas com a API TESS, verifique o status do serviço
- Logs detalhados podem ser ativados definindo `LOG_LEVEL=debug` no arquivo `.env`

## Licença

MIT 