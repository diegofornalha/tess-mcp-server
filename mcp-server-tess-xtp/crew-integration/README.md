# TESS-MCP com CrewAI

Esta integração permite utilizar as ferramentas TESS disponíveis através do servidor MCP usando uma equipe de agentes inteligentes criados com o framework CrewAI.

## Arquitetura

```
Cliente (Streamlit) → CrewAI + Agentes → SDK Tools → MCP Server → TESS API
```

Esta arquitetura proporciona:
- **Modularidade extrema**: Cada componente evolui independentemente
- **Orquestração inteligente**: Agentes especializados trabalhando em conjunto
- **Memória integrada**: Persistência de contexto entre interações
- **Fácil configuração**: Definição de agentes e tarefas em YAML

## Componentes

### 1. Agentes CrewAI
- **Agente Principal**: Coordena a execução e interpreta solicitações
- **Especialista TESS**: Executa as ferramentas TESS com precisão
- **Especialista em Conteúdo**: Formata os resultados para o usuário

### 2. Wrapper MCP-TESS
- Adapta as ferramentas TESS disponíveis via MCP para uso com CrewAI
- Converte esquemas JSON em modelos Pydantic compatíveis

### 3. Interface Streamlit
- Interface amigável para interagir com os agentes CrewAI
- Histórico de consultas e visualização de resultados

## Configuração

1. Certifique-se de que o servidor MCP-TESS esteja em execução:
   ```bash
   # No diretório raiz do projeto
   npm run start
   ```

2. Configure o ambiente para a integração CrewAI:
   ```bash
   cd crew-integration
   ./setup.sh
   ```

3. Edite o arquivo `.env` com suas configurações (criado automaticamente pelo script de configuração)

## Uso

Após configurar o ambiente, você pode iniciar a interface Streamlit:
```bash
cd crew-integration
source venv/bin/activate
streamlit run app.py
```

Ou use o script de configuração que oferece a opção de iniciar o Streamlit:
```bash
./setup.sh
# Selecione a opção 1 quando solicitado
```

## Personalização

### Adicionar ou modificar agentes
Edite o arquivo `config/agents.yaml` para adicionar ou modificar as definições dos agentes.

### Modificar tarefas
Edite o arquivo `config/tasks.yaml` para alterar o fluxo de trabalho ou adicionar novas tarefas.

### Integrar com outros provedores
Por padrão, o sistema utiliza o OpenAI como provedor LLM, mas está configurado para trabalhar com Arcee também. Defina `TESS_CREW_PROVIDER=arcee` no arquivo `.env` para utilizar o Arcee como provedor.

## Requisitos

- Python 3.8 ou superior
- Node.js 14 ou superior (para o servidor MCP-TESS)
- Servidor MCP-TESS em execução
- Chave de API OpenAI ou Arcee (dependendo do provedor configurado)

## Desenvolvimento

Os principais arquivos para desenvolvimento são:

- `tess_crew.py`: Classe principal da integração com CrewAI
- `tools/mcpx_tools.py`: Wrapper para integração com ferramentas MCP-TESS
- `app.py`: Interface Streamlit
- `config/agents.yaml` e `config/tasks.yaml`: Configurações dos agentes e tarefas 