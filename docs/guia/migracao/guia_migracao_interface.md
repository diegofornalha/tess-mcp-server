# Guia de Migração para a Camada de Interface

Este documento fornece orientações para migrar os componentes de interface do usuário (UI) existentes para a nova estrutura arquitetural, conforme definido no documento de arquitetura de referência.

## Visão Geral

A arquitetura de referência define uma clara separação entre a camada de interface e as outras camadas do sistema. Esta separação é fundamental para:

1. **Desacoplar a UI da lógica de negócio**
2. **Facilitar testes automatizados**
3. **Permitir múltiplas interfaces para o mesmo sistema**
4. **Simplificar manutenção e evolução**

## Estrutura Alvo

A nova estrutura da camada de interface deve seguir este padrão:

```
interfaces/
├── cli/              # Interface de linha de comando
│   ├── commands/     # Comandos disponíveis na CLI
│   ├── formatters/   # Formatadores de saída (tabelas, JSON, etc.)
│   └── validators/   # Validação de entrada do usuário
├── api/              # Interface de API REST (se aplicável)
│   ├── routes/       # Definição de rotas da API
│   ├── schemas/      # Esquemas de validação
│   └── middlewares/  # Middlewares da API
└── controllers/      # Controladores que coordenam fluxos de UI
```

## Princípios de Migração

### 1. Responsabilidade Única

Cada componente da interface deve ter uma única responsabilidade:
- **Comandos CLI**: Lidar com argumentos e opções da linha de comando
- **Controladores**: Coordenar o fluxo de controle e chamar casos de uso
- **Formatadores**: Formatar dados para apresentação ao usuário

### 2. Inversão de Dependência

A camada de interface deve depender de abstrações da camada de aplicação, não de implementações concretas:

```python
# interfaces/cli/commands/agent_commands.py

class AgentCommands:
    def __init__(self, agent_use_case):
        self.agent_use_case = agent_use_case  # Injeção de dependência
        
    def list_agents(self, limit=10, format="table"):
        # Obter dados da camada de aplicação
        agents = self.agent_use_case.list_agents(limit)
        
        # Formatar para apresentação
        if format == "table":
            return self._format_as_table(agents)
        elif format == "json":
            return self._format_as_json(agents)
```

### 3. Validação de Entrada

Toda validação de entrada do usuário deve ocorrer na camada de interface antes de passar para a aplicação:

```python
def execute_agent(self, agent_id, params):
    # Validar entrada
    if not agent_id:
        raise ValueError("ID do agente é obrigatório")
        
    # Limpar e normalizar parâmetros
    cleaned_params = self._clean_params(params)
    
    # Passar para a camada de aplicação
    return self.agent_use_case.execute_agent(agent_id, cleaned_params)
```

## Passos para Migração

### Fase 1: Análise dos Componentes Existentes

1. **Identificar Componentes de Interface**:
   - Comandos CLI em `src/commands/`
   - Interface de usuário em `crew/`
   - Outros elementos de UI espalhados pelo código

2. **Documentar Dependências**:
   - Quais serviços e providers cada componente utiliza
   - Quais partes da lógica de negócio estão misturadas na UI

### Fase 2: Criar Estrutura de Diretórios

1. **Estabelecer Nova Estrutura**:
   - Criar diretórios conforme a estrutura alvo
   - Configurar `__init__.py` para exposição correta de módulos

2. **Definir Controladores**:
   - Criar controladores para orquestrar fluxos de UI
   - Estabelecer interfaces para injeção de dependências

### Fase 3: Implementar Interface CLI

1. **Migrar Comandos**:
   - Criar novos comandos em `interfaces/cli/commands/`
   - Refatorar para depender de casos de uso, não de implementações diretas

2. **Implementar Formatadores**:
   - Extrair lógica de formatação para classes dedicadas
   - Suportar múltiplos formatos de saída (texto, JSON, tabelas)

### Fase 4: Migrar Código Existente

1. **Migração Gradual**:
   - Começar com comandos menos complexos
   - Implementar adaptadores temporários se necessário

2. **Testes de Regressão**:
   - Garantir que funcionalidades existentes continuem funcionando
   - Implementar testes automatizados para novas interfaces

## Exemplos Práticos

### Antes da Migração:

```python
# src/commands/chat.py
import click
from src.providers.tess_provider import TessProvider

@click.command()
@click.option('--agent-id', required=True, help='ID do agente')
def chat(agent_id):
    """Inicia um chat com um agente TESS."""
    provider = TessProvider()
    agents = provider.list_agents()
    
    # Verifica se o agente existe
    agent = next((a for a in agents if a['id'] == agent_id), None)
    if not agent:
        click.echo("Agente não encontrado.")
        return
    
    # Lógica de processamento e execução
    # ...
```

### Depois da Migração:

```python
# interfaces/cli/commands/chat_command.py
import click
from application.use_cases.chat_use_case import ChatUseCase

class ChatCommand:
    def __init__(self, chat_use_case: ChatUseCase):
        self.chat_use_case = chat_use_case
    
    @click.command()
    @click.option('--agent-id', required=True, help='ID do agente')
    def chat(self, agent_id):
        """Inicia um chat com um agente TESS."""
        try:
            # Delegar para o caso de uso na camada de aplicação
            chat_session = self.chat_use_case.start_chat(agent_id)
            
            # Loop de interação com formatação apropriada
            # ...
            
        except ValueError as e:
            click.echo(f"Erro: {str(e)}")
        except Exception as e:
            click.echo(f"Erro inesperado: {str(e)}")

# interfaces/cli/main.py
from infrastructure.providers import create_provider
from application.use_cases.chat_use_case import ChatUseCase
from interfaces.cli.commands.chat_command import ChatCommand

def setup_cli():
    # Configurar dependências
    tess_provider = create_provider("tess")
    chat_use_case = ChatUseCase(tess_provider)
    
    # Configurar comandos
    chat_command = ChatCommand(chat_use_case)
    
    # Registrar comandos no CLI
    # ...
```

## Padrões a Adotar

### 1. Command Pattern

Usar o padrão Command para encapsular solicitações como objetos:

```python
class ListAgentsCommand:
    def __init__(self, agent_use_case):
        self.agent_use_case = agent_use_case
    
    def execute(self, page=1, per_page=20, format="table"):
        # Implementação
```

### 2. Formatadores

Separar a lógica de formatação em classes específicas:

```python
class TableFormatter:
    def format_agents(self, agents):
        # Formatar agentes como tabela
        # ...

class JsonFormatter:
    def format_agents(self, agents):
        # Formatar agentes como JSON
        # ...
```

### 3. Factory para Componentes de Interface

Usar factories para criar componentes de interface com suas dependências:

```python
def create_cli_app():
    # Configurar providers
    tess_provider = create_provider("tess")
    
    # Configurar casos de uso
    agent_use_case = AgentUseCase(tess_provider)
    
    # Configurar comandos
    agent_command = AgentCommand(agent_use_case)
    
    # Configurar aplicação CLI
    app = CliApp()
    app.register_command("agent", agent_command)
    
    return app
```

## Checklist de Migração

- [ ] Componente de interface não contém lógica de negócio
- [ ] Validação de entrada acontece na camada de interface
- [ ] Formatação de saída é feita por formatadores dedicados
- [ ] Interface depende apenas de abstrações da aplicação
- [ ] Tratamento de erros específicos da interface é implementado
- [ ] Testes unitários para componentes de interface estão implementados

## Desafios Comuns e Soluções

### Desafio: Lógica de Negócio na UI

**Solução**: Identificar lógica de negócio em comandos CLI e movê-la para a camada de aplicação como casos de uso.

### Desafio: Dependências Diretas de Provedores

**Solução**: Substituir dependências diretas por injeção de dependência de interfaces abstratas.

### Desafio: Formatação Misturada com Lógica

**Solução**: Extrair lógica de formatação para classes dedicadas que podem ser injetadas ou selecionadas dinamicamente.

## Próximos Passos

1. Realizar inventário de componentes de interface existentes
2. Definir prioridades para migração (começar com componentes mais simples)
3. Implementar infraestrutura básica para nova camada de interface
4. Criar primeiros componentes migrados como prova de conceito
5. Estabelecer cronograma para migração completa 