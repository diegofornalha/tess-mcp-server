# Guia de Refatoração para a Camada de Domínio

Este documento fornece diretrizes para a refatoração da camada de domínio, alinhando o projeto com os princípios de Clean Architecture e Domain-Driven Design (DDD) conforme definido no documento de arquitetura de referência.

## Princípios Orientadores

A refatoração da camada de domínio deve seguir estes princípios:

1. **Isolamento Completo**: O domínio não deve depender de nenhuma camada externa
2. **Regras Centrais no Domínio**: Todas as regras de negócio devem residir no domínio
3. **Interfaces Bem Definidas**: Interfaces claras para serviços externos
4. **Entidades Ricas**: Entidades com comportamento, não apenas dados
5. **Linguagem Ubíqua**: Usar termos do negócio no código

## Abordagem Faseada

### Fase 1: Análise do Código Existente

1. **Identificar Lógica de Domínio em Outras Camadas**:
   - Buscar em `src/`, `tools/`, `crew/` por lógica que pertence ao domínio
   - Documentar responsabilidades e dependências

2. **Mapear Conceitos do Domínio**:
   - Identificar entidades, objetos de valor, serviços, etc.
   - Definir glossário com termos da linguagem ubíqua

### Fase 2: Definição de Interfaces

1. **Definir Novas Interfaces**:
   - Para repositórios (persistência)
   - Para provedores (serviços externos)
   - Para serviços de domínio

2. **Atualizar Interfaces Existentes**:
   - Revisar interfaces existentes para garantir que estão alinhadas com os princípios

### Fase 3: Implementação das Entidades e Valores

1. **Implementar Entidades**:
   - Criar classes para conceitos centrais do negócio
   - Implementar comportamento (métodos) relevante
   - Garantir encapsulamento e validações

2. **Implementar Objetos de Valor**:
   - Identificar conceitos sem identidade
   - Implementar como objetos imutáveis

### Fase 4: Migração de Lógica de Negócio

1. **Mover Regras de Negócio**:
   - De `src/`, `tools/`, `crew/` para o domínio
   - Adaptar para usar interfaces ao invés de implementações concretas

2. **Refatorar Camada de Aplicação**:
   - Ajustar para usar novas entidades e interfaces
   - Implementar novos casos de uso conforme necessário

### Fase 5: Testes

1. **Implementar Testes Unitários**:
   - Para entidades e objetos de valor
   - Para serviços de domínio
   - Para regras de negócio

## Exemplos Práticos

### Antes da Refatoração (Código em src/tools/mcp_nl_processor.py)

```python
def process_command(text):
    # Lógica de processamento misturada com infraestrutura
    config = get_config_from_file()
    if "listar agentes" in text:
        provider = TessProvider()
        return provider.list_agents()
    # ...
```

### Depois da Refatoração

```python
# domain/services/command_processor.py
class CommandProcessorService:
    def __init__(self, tess_provider_interface):
        self.tess_provider = tess_provider_interface
        
    def process_command(self, text):
        # Lógica pura de domínio
        if self.is_list_agents_command(text):
            return self.tess_provider.list_agents()
        # ...
    
    def is_list_agents_command(self, text):
        # Lógica de domínio para interpretar comandos
        return any(pattern in text.lower() for pattern in ["listar agentes", "ver agentes", "mostrar agentes"])
```

## Diretrizes para Refatoração

### 1. Identificando Código para Refatorar

Busque código com estas características:
- Implementa regras de negócio
- Define conceitos centrais do sistema
- Contém lógica independente de UI ou infraestrutura

### 2. Criando Entidades e Objetos de Valor

**Entidades**: Têm identidade e ciclo de vida
```python
class Agent:
    def __init__(self, id, name, description):
        self._id = id
        self._name = name
        self._description = description
        self._is_active = True
    
    def activate(self):
        self._is_active = True
    
    def deactivate(self):
        self._is_active = False
    
    def execute(self, params):
        if not self._is_active:
            raise AgentInactiveError(f"Agent {self._name} is inactive")
        # Lógica para execução
```

**Objetos de Valor**: Imutáveis, sem identidade
```python
class CommandPattern:
    def __init__(self, pattern, examples):
        self._pattern = pattern
        self._examples = tuple(examples)  # Imutável
    
    def matches(self, text):
        # Lógica para verificar se o texto corresponde ao padrão
        return self._pattern in text
```

### 3. Definindo Interfaces

```python
from abc import ABC, abstractmethod

class AgentRepositoryInterface(ABC):
    @abstractmethod
    def get_by_id(self, agent_id):
        pass
    
    @abstractmethod
    def list_all(self, filter_criteria=None):
        pass
    
    @abstractmethod
    def save(self, agent):
        pass
```

## Padrões a Evitar

1. **Anêmico vs. Rico**: Evite modelos de domínio anêmicos (apenas getters/setters)
2. **Acoplamento com Infraestrutura**: Evite imports de frameworks no domínio
3. **Vazamento de Responsabilidade**: Mantenha a lógica de domínio no domínio
4. **Interfaces Incorretas**: Defina interfaces para abstrair o que realmente varia

## Checklist de Revisão

- [ ] Código de domínio não tem dependências externas
- [ ] Entidades encapsulam dados e comportamento
- [ ] Interfaces definem contratos claros
- [ ] Linguagem do código reflete a linguagem do negócio
- [ ] Testes unitários cobrem regras de negócio
- [ ] Conceitos do domínio são coesos e focados
- [ ] Responsabilidades estão claramente delimitadas

## Próximos Passos

1. Realizar inventário completo de código de domínio espalhado
2. Definir plano detalhado de migração por componente
3. Implementar refatoração em pequenos incrementos testáveis
4. Revisar e validar com a equipe de negócio 