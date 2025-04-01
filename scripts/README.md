# Scripts Utilitários para TESS-MCP

Este diretório contém scripts utilitários para configuração, inicialização e manutenção do servidor TESS-MCP.

## Scripts disponíveis

### `setup.sh`

Script de configuração inicial do servidor TESS-MCP.

**Descrição**: Este script prepara o ambiente para execução do servidor TESS-MCP, verificando dependências, instalando pacotes necessários e configurando arquivos básicos.

**Uso**:
```bash
./scripts/setup.sh
```

**Funcionalidades**:
- Verifica a instalação do Node.js e NPM
- Instala dependências do projeto via NPM
- Cria arquivo `.env` a partir do `.env.example`, ou cria um básico caso não exista
- Verifica/cria o diretório `public` com uma página HTML de exemplo
- Torna os scripts executáveis

**Requisitos**:
- Node.js instalado
- NPM instalado
- Permissões de escrita no diretório do projeto

### `start.sh`

Script para iniciar o servidor TESS-MCP.

**Descrição**: Inicia o servidor TESS-MCP, verificando configurações e dependências antes da execução.

**Uso**:
```bash
# Iniciar em modo desenvolvimento (com hot-reload)
./scripts/start.sh

# Iniciar em modo produção (sem hot-reload)
./scripts/start.sh --prod
```

**Funcionalidades**:
- Verifica a presença do Node.js
- Instala dependências caso não estejam instaladas
- Verifica a presença e configuração do arquivo `.env`
- Inicia o servidor com nodemon (desenvolvimento) ou node (produção)

**Requisitos**:
- Setup completo via `setup.sh`
- Arquivo `.env` configurado com a API key do TESS

## Como usar o servidor TESS-MCP

O servidor TESS-MCP integra a API TESS com o protocolo MCP (Model Context Protocol), permitindo:

1. **Acesso às ferramentas TESS via MCP**: Use agentes TESS em modelos de IA compatíveis com MCP
2. **Interface WebSocket**: Comunicação em tempo real para monitoramento de execuções
3. **Cliente de demonstração**: Interface web simples para testar as ferramentas

### Fluxo de trabalho recomendado

1. Execute `./scripts/setup.sh` para configurar o ambiente
2. Edite o arquivo `.env` para adicionar sua API Key do TESS
3. Execute `./scripts/start.sh` para iniciar o servidor
4. Acesse `http://localhost:3001` para testar o cliente de demonstração

### Endpoints disponíveis

- **GET /health**: Verifica o status do servidor
- **POST /tools/list**: Lista as ferramentas TESS disponíveis (protocolo MCP)
- **POST /tools/call**: Executa uma ferramenta TESS (protocolo MCP)

### Ferramentas disponíveis

- **tess.list_agents**: Lista os agentes disponíveis
- **tess.get_agent**: Obtém detalhes de um agente específico
- **tess.execute_agent**: Executa um agente TESS
- **tess.upload_file**: Faz upload de um arquivo para o TESS

## Solução de problemas

**Problema**: Servidor não inicia
- Verifique se o arquivo `.env` existe e contém a API Key do TESS
- Certifique-se de que as dependências estão instaladas (`npm install`)
- Verifique se a porta 3001 está disponível

**Problema**: Erro de autenticação do TESS
- Verifique a API Key no arquivo `.env`
- Certifique-se de que sua API Key tem permissões adequadas

**Problema**: Nodemon não está instalado
- Execute `npm install -g nodemon` para instalar globalmente, ou
- O servidor iniciará em modo padrão (sem hot-reload)

## Contribuição

Para contribuir com o desenvolvimento, clone o repositório e execute o setup:

```bash
git clone [URL_DO_REPOSITÓRIO]
cd mcp-server-tess
./scripts/setup.sh
``` 