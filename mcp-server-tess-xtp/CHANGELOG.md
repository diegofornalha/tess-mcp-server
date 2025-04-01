# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2024-04-01

### Adicionado
- Versão inicial do servidor TESS-MCP
- Implementação das ferramentas TESS via MCP:
  - `tess.list_agents`: Lista os agentes disponíveis no TESS
  - `tess.get_agent`: Obtém detalhes de um agente específico
  - `tess.execute_agent`: Executa um agente TESS
  - `tess.upload_file`: Faz upload de um arquivo para o TESS
- Interface WebSocket para monitoramento em tempo real
- Cliente de demonstração HTML para testes interativos
- Scripts de configuração e inicialização inspirados no DesktopCommanderMCP
- Exemplo de integração para clientes Node.js
- Configuração para publicação no Smithery
- Documentação completa com exemplos de uso

### Melhorado
- Estrutura de diretórios organizada
- Tratamento robusto de erros
- Documentação abrangente no README.md
- Configuração simplificada com .env.example

### Corrigido
- Problemas de inicialização em diferentes ambientes
- Questões de compatibilidade com diferentes versões da API TESS
- Problemas de CORS para comunicação entre domínios