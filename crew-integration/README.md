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
- **Seleção de modelo flexível**: Escolha entre diferentes modelos de LLM para cada consulta

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

### Integrar com múltiplos provedores

O sistema agora suporta múltiplos provedores de LLM com a seguinte ordem de prioridade:

1. **TESS** (via API OpenAI-compatível) - provedor principal
2. **Arcee** - primeiro fallback se TESS não estiver disponível
3. **OpenAI** - segundo fallback

Configure os provedores no arquivo `.env`:

```
# Configuração do TESS (prioridade 1)
TESS_API_KEY=your-tess-api-key
TESS_API_URL=https://tess.pareto.io/api
TESS_AGENT_ID=8794  # ID do agente padrão

# Configuração do Arcee (fallback 1)
ARCEE_API_KEY=your-arcee-api-key
ARCEE_MODEL=auto

# Configuração do OpenAI (fallback 2)
OPENAI_API_KEY=sk-your-openai-api-key
```

### Seleção de Modelo

A interface Streamlit agora permite selecionar o modelo específico para cada consulta, bem como ajustar a temperatura. Os modelos disponíveis incluem:

- **auto** - Permite que o sistema escolha automaticamente o melhor modelo disponível
- gpt-4o, gpt-4o-mini
- tess-ai-light, tess-ai-3
- gpt-o1-preview, gpt-o1-mini
- gemini-2.0-flash, gemini-1.5-flash, gemini-1.5-pro
- claude-3-5-haiku-latest, claude-3-5-sonnet-latest, claude-3-opus
- meta-llama-3.1-405b-instruct, meta-llama-3-70b-instruct

Quando a opção "auto" é selecionada, o sistema escolherá o modelo mais adequado com base na disponibilidade e nas políticas de roteamento do TESS. Para outros modelos específicos, o sistema tentará usar o modelo solicitado, mas pode fazer fallback para outro modelo se necessário.

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

### Integrar com múltiplos provedores

O sistema agora suporta múltiplos provedores de LLM com a seguinte ordem de prioridade:

1. **TESS** (via API OpenAI-compatível) - provedor principal
2. **Arcee** - primeiro fallback se TESS não estiver disponível
3. **OpenAI** - segundo fallback

Configure os provedores no arquivo `.env`:

```
# Configuração do TESS (prioridade 1)
TESS_API_KEY=your-tess-api-key
TESS_API_URL=https://tess.pareto.io/api
TESS_AGENT_ID=1234  # Substitua pelo ID correto do seu agente

# Configuração do Arcee (fallback 1)
ARCEE_API_KEY=your-arcee-api-key
ARCEE_MODEL=auto
```

#### Suporte flexível para Arcee

O sistema agora suporta o Arcee de duas formas:

1. **Usando a API Key do Arcee** - Configure a variável `ARCEE_API_KEY` no arquivo `.env`
2. **Usando a CLI do Arcee local** - Se você tem o Arcee CLI instalado, o sistema o utilizará automaticamente

Você pode usar qualquer uma das opções ou ambas. Se ambas estiverem configuradas, o sistema tentará primeiro a API Key e, em caso de falha, utilizará a CLI local. Isso torna o sistema mais resiliente e permite múltiplas configurações. 