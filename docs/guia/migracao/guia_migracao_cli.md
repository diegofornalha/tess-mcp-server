# Guia de Migração da Interface CLI

Este documento descreve o processo para migrar a interface de linha de comando (CLI) para a nova arquitetura do projeto, seguindo os princípios de Clean Architecture e Domain-Driven Design.

## Objetivo

O objetivo deste guia é fornecer um plano claro para migrar a interface CLI de sua implementação atual para uma estrutura mais modular e alinhada com os princípios arquiteturais estabelecidos, permitindo:

1. Separação clara entre interface do usuário e lógica de negócios
2. Injeção de dependências para facilitar testes
3. Reuso dos serviços de domínio e aplicação
4. Evolução sustentável da aplicação CLI

## Estado Atual

Atualmente, a interface CLI está implementada de forma acoplada com a lógica de negócios, com diversos componentes interagindo diretamente com implementações concretas em vez de abstrações.

Principais problemas:
- Acoplamento direto com provedores específicos
- Ausência de separação clara entre comandos e lógica de negócios
- Dificuldade para testes automatizados
- Replicação de lógica entre a CLI e outros componentes

## Arquitetura Alvo

Na arquitetura alvo, a CLI seguirá a estrutura:

```
application/
  cli/
    commands/       # Definição dos comandos CLI
    adapters/       # Adaptadores para interfaces externas
    formatters/     # Formatadores de saída (texto, json, etc)
    validators/     # Validadores de entrada
    config/         # Configurações da CLI
    main.py         # Ponto de entrada da CLI
```

A CLI utilizará o padrão Command para encapsular solicitações como objetos, permitindo:
- Parametrização de clientes com diferentes solicitações
- Enfileiramento de solicitações
- Implementação de sistema de log para operações
- Suporte à operações que podem ser desfeitas

## Plano de Migração

### Fase 1: Análise e Preparação

1. **Mapear Comandos Existentes**
   - Identificar todos os comandos CLI existentes
   - Documentar o comportamento e dependências de cada comando
   - Identificar padrões e oportunidades de refatoração

2. **Definir Interfaces de Serviço**
   - Criar interfaces para os serviços que a CLI consumirá
   - Implementar adaptadores para as implementações existentes

3. **Desenvolver Estrutura dos Comandos**
   - Criar classes base para comandos CLI
   - Implementar mecanismos de registro de comandos
   - Desenvolver sistema de ajuda e documentação integrado

### Fase 2: Implementação Gradual

1. **Migrar Comandos Simples**
   - Começar com comandos que têm menos dependências
   - Implementar testes para cada comando migrado
   - Validar comportamento idêntico entre versões

2. **Migrar Comandos Complexos**
   - Refatorar comandos com múltiplas dependências
   - Implementar injeção de dependências
   - Garantir retrocompatibilidade

3. **Implementar Sistema de Configuração**
   - Desenvolver mecanismo de carregamento de configuração
   - Migrar configurações hard-coded para arquivos de configuração
   - Implementar validação de configuração

### Fase 3: Testes e Finalização

1. **Testes Abrangentes**
   - Criar testes de integração para toda a CLI
   - Implementar testes end-to-end simulando uso real
   - Validar todos os fluxos de comando

2. **Documentação e Exemplos**
   - Atualizar documentação de uso da CLI
   - Criar exemplos para cenários comuns
   - Documentar processo de extensão da CLI

3. **Depreciação da Implementação Anterior**
   - Implementar redirecionamento da CLI antiga para a nova
   - Definir período de depreciação
   - Comunicar mudanças aos usuários

## Implementação Técnica

### Exemplo: Estrutura de Comando

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from domain.services.agent_service import AgentService

class Command(ABC):
    """Classe base para comandos da CLI."""
    
    @abstractmethod
    def execute(self, args: Dict[str, Any]) -> int:
        """Executa o comando com os argumentos fornecidos."""
        pass
    
    @property
    @abstractmethod
    def help(self) -> str:
        """Retorna a mensagem de ajuda do comando."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Retorna o nome do comando."""
        pass

class ListAgentsCommand(Command):
    """Comando para listar agentes disponíveis."""
    
    def __init__(self, agent_service: AgentService):
        self.agent_service = agent_service
    
    @property
    def name(self) -> str:
        return "list-agents"
    
    @property
    def help(self) -> str:
        return "Lista todos os agentes disponíveis no sistema."
    
    def execute(self, args: Dict[str, Any]) -> int:
        try:
            agents = self.agent_service.list_agents()
            for agent in agents:
                print(f"ID: {agent.id}, Nome: {agent.name}")
            return 0
        except Exception as e:
            print(f"Erro ao listar agentes: {e}")
            return 1
```

### Exemplo: Registro de Comandos

```python
class CommandRegistry:
    """Registro de comandos disponíveis na CLI."""
    
    def __init__(self):
        self._commands: Dict[str, Command] = {}
    
    def register(self, command: Command) -> None:
        """Registra um novo comando."""
        self._commands[command.name] = command
    
    def get_command(self, name: str) -> Optional[Command]:
        """Obtém um comando pelo nome."""
        return self._commands.get(name)
    
    def list_commands(self) -> List[Command]:
        """Lista todos os comandos registrados."""
        return list(self._commands.values())
```

### Exemplo: Ponto de Entrada da CLI

```python
def setup_commands(registry: CommandRegistry, service_factory) -> None:
    """Configura os comandos disponíveis na CLI."""
    # Inicializa serviços necessários
    agent_service = service_factory.create_agent_service()
    
    # Registra comandos
    registry.register(ListAgentsCommand(agent_service))
    registry.register(ExecuteAgentCommand(agent_service))
    # ...

def main():
    """Ponto de entrada principal da CLI."""
    # Inicializa o registro de comandos
    registry = CommandRegistry()
    
    # Configura o factory de serviços
    service_factory = ServiceFactory()
    
    # Configura os comandos
    setup_commands(registry, service_factory)
    
    # Processa argumentos da linha de comando
    args = parse_arguments()
    
    # Obtém e executa o comando
    command = registry.get_command(args.command)
    if command:
        exit_code = command.execute(vars(args))
        sys.exit(exit_code)
    else:
        print(f"Comando desconhecido: {args.command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Cronograma Recomendado

1. **Fase 1: Análise e Preparação** - 2 semanas
   - Mapeamento de comandos existentes - 3 dias
   - Definição de interfaces de serviço - 5 dias
   - Desenvolvimento da estrutura de comandos - 2 dias

2. **Fase 2: Implementação Gradual** - 4 semanas
   - Migração de comandos simples - 1 semana
   - Migração de comandos complexos - 2 semanas
   - Implementação do sistema de configuração - 1 semana

3. **Fase 3: Testes e Finalização** - 2 semanas
   - Testes abrangentes - 1 semana
   - Documentação e exemplos - 3 dias
   - Depreciação da implementação anterior - 2 dias

## Métricas de Sucesso

- 100% dos comandos existentes migrados
- Cobertura de testes superior a 80%
- Zero regressões funcionais após a migração
- Documentação completa para todos os comandos
- Feedback positivo dos usuários da CLI

## Considerações de Compatibilidade

Para garantir uma transição suave, recomendamos:

1. Manter aliases para comandos populares, preservando a sintaxe atual
2. Implementar redirecionamento automático da CLI antiga para a nova
3. Fornecer mensagens claras quando comportamentos mudarem
4. Incluir exemplos de migração para casos de uso comuns

## Conclusão

A migração da interface CLI para a nova arquitetura é um passo importante para garantir a manutenibilidade e extensibilidade do projeto a longo prazo. Seguindo este guia, a equipe poderá realizar esta migração de forma gradual e controlada, minimizando o impacto para os usuários enquanto implementa melhorias significativas na estrutura do código.
