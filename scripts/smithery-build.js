/**
 * Script para preparar o projeto para publicação no Smithery
 * Este script gera o arquivo smithery.yaml necessário
 */

const fs = require('fs');
const path = require('path');

// Caminho para a raiz do projeto
const ROOT_DIR = path.join(__dirname, '..');

// Configuração do Smithery
const smitheryConfig = {
  name: 'mcp-server-tess-xtp',
  description: 'Servidor MCP para integração com a API TESS, permitindo utilizar agentes TESS via MCP.',
  version: '1.0.0',
  main: './mcp-adapter.js',
  license: 'MIT',
  author: 'TESS Team',
  homepage: 'https://github.com/diegofornalha/mcp-server-tess-xtp',
  repository: 'https://github.com/diegofornalha/mcp-server-tess-xtp',
  configSchema: {
    type: 'object',
    properties: {
      TESS_API_KEY: {
        type: 'string',
        description: 'Chave de API TESS (obrigatória)'
      },
      TESS_API_URL: {
        type: 'string',
        description: 'URL da API TESS (opcional)',
        default: 'https://tess.pareto.io/api'
      },
      PORT: {
        type: 'number',
        description: 'Porta para o servidor MCP',
        default: 3001
      }
    },
    required: ['TESS_API_KEY']
  },
  dependencies: [
    'axios',
    'cors',
    'dotenv',
    'express',
    'form-data',
    'socket.io'
  ],
  engines: {
    node: '>=18.0.0'
  },
  keywords: [
    'tess',
    'mcp',
    'ai',
    'model-context-protocol',
    'agent',
    'smithery'
  ]
};

// Converter para YAML
const yaml = `# Configuração do Smithery para mcp-server-tess-xtp
name: ${smitheryConfig.name}
description: ${smitheryConfig.description}
version: ${smitheryConfig.version}
main: ${smitheryConfig.main}
license: ${smitheryConfig.license}
author: ${smitheryConfig.author}
homepage: ${smitheryConfig.homepage}
repository: ${smitheryConfig.repository}

# Esquema de configuração
configSchema:
  type: object
  properties:
    TESS_API_KEY:
      type: string
      description: "Chave de API TESS (obrigatória)"
    TESS_API_URL:
      type: string
      description: "URL da API TESS (opcional)"
      default: "https://tess.pareto.io/api"
    PORT:
      type: number
      description: "Porta para o servidor MCP"
      default: 3001
  required:
    - TESS_API_KEY

# Dependências e requisitos
engines:
  node: ">=18.0.0"
keywords:
  - tess
  - mcp
  - ai
  - model-context-protocol
  - agent
  - smithery
`;

// Escrever o arquivo smithery.yaml
fs.writeFileSync(path.join(ROOT_DIR, 'smithery.yaml'), yaml);

console.log('✅ Arquivo smithery.yaml gerado com sucesso!');
console.log('');
console.log('Para publicar no Smithery:');
console.log('1. Certifique-se de ter feito login no Smithery CLI: npx @smithery/cli@latest login');
console.log('2. Execute: npm run smithery:publish');
console.log('');
console.log('Para testar localmente antes de publicar:');
console.log('npx @smithery/cli@latest run .'); 