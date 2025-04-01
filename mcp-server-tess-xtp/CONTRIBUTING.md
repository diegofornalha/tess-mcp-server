# Contribuindo para o TESS-MCP Server

Obrigado pelo interesse em contribuir para o TESS-MCP Server! Este documento fornece diretrizes e informações para ajudar você a contribuir com este projeto.

## Como Contribuir

Existem várias maneiras de contribuir:

1. **Reportar bugs**: Crie uma issue descrevendo o bug, como reproduzi-lo e o impacto
2. **Sugerir melhorias**: Crie uma issue propondo novas funcionalidades ou melhorias
3. **Enviar correções**: Faça um fork do repositório, crie uma branch para suas alterações e envie um pull request
4. **Melhorar a documentação**: Atualize o README, adicione exemplos, corrija erros ou adicione detalhes

## Fluxo de Trabalho para Contribuições

1. **Fork o repositório** para sua conta GitHub
2. **Clone seu fork** localmente:
   ```bash
   git clone https://github.com/seu-usuario/tess-mcp-server.git
   cd tess-mcp-server
   ```
3. **Crie uma branch** para sua contribuição:
   ```bash
   git checkout -b feature/sua-funcionalidade
   ```
4. **Faça suas alterações** seguindo as diretrizes de código
5. **Teste suas alterações**:
   ```bash
   npm test  # Se tivermos testes automatizados
   # Ou teste manualmente iniciando o servidor
   ./scripts/start.sh
   ```
6. **Faça commit das alterações**:
   ```bash
   git commit -m "Adiciona: descrição concisa da alteração"
   ```
7. **Envie para seu fork**:
   ```bash
   git push origin feature/sua-funcionalidade
   ```
8. **Crie um Pull Request** do seu fork para o repositório original

## Diretrizes de Código

- Mantenha o código limpo e legível
- Siga o estilo de código atual do projeto
- Adicione comentários para explicar código complexo
- Mantenha o código modular e reutilizável
- Tente manter retrocompatibilidade sempre que possível

## Diretrizes para Commits

- Use mensagens de commit claras e descritivas
- Comece com um verbo no imperativo: "Adiciona", "Corrige", "Atualiza", etc.
- Primeira linha: resumo conciso (até 50 caracteres)
- Se necessário, adicione um corpo detalhado após uma linha em branco

## Pull Requests

- Descreva claramente o que o PR faz e por quê
- Vincule a issues relacionadas usando #número_da_issue
- Certifique-se de que o código passou em todos os testes
- Mantenha o PR focado em uma única funcionalidade ou correção

## Configuração de Desenvolvimento

1. Clone o repositório:
   ```bash
   git clone https://github.com/diegofornalha/tess-mcp-server.git
   cd tess-mcp-server
   ```

2. Instale as dependências:
   ```bash
   npm install
   ```

3. Configure o ambiente:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

4. Execute o servidor em modo desenvolvimento:
   ```bash
   ./scripts/start.sh
   ```

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença MIT do projeto.

## Dúvidas?

Se você tiver dúvidas sobre como contribuir, sinta-se à vontade para abrir uma issue perguntando. Estaremos felizes em ajudar!