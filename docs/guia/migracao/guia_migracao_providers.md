# Guia de Migração: Provedores de Serviços

Este documento fornece orientações para migrar o código que utiliza os provedores em `src/providers` para usar as novas implementações em `infrastructure/providers`, conforme a arquitetura de referência.

## Visão Geral

Como parte da reorganização arquitetural do projeto `crew_ai_tess_pareto`, os provedores para serviços externos (TESS, MCP, etc.) foram movidos para a camada de infraestrutura e implementados seguindo interfaces bem definidas na camada de domínio.

### Benefícios da Nova Estrutura

1. **Separação de Responsabilidades**: Implementações concretas isoladas da lógica de negócio
2. **Abstração Adequada**: Interfaces no domínio definem contratos sem detalhes de implementação
3. **Manutenibilidade**: Mudanças em uma implementação não afetam outras partes do sistema
4. **Testabilidade**: Facilidade para mockar provedores em testes
5. **Extensibilidade**: Adicionar novos provedores sem modificar o código existente

## O Que Mudou

| Componente Antigo | Componente Novo | Observações |
|-------------------|-----------------|-------------|
| `src/providers/tess_provider.py` | `infrastructure/providers/tess_provider.py` | Implementa `TessProviderInterface` |
| `src/providers/mcp_provider.py` | `infrastructure/providers/mcp_provider.py` | Implementa `MCPProviderInterface` |
| Criação direta de instâncias | `ProviderFactory` e funções helper | Uso de padrão Factory para criação de provedores |

## Como Migrar

### 1. Importações

#### Antes:

```python
from src.providers import TessProvider, MCPProvider

# Criar instância diretamente
provider = TessProvider()
```

#### Depois:

```python
from infrastructure.providers import create_provider, TessProvider

# Opção 1: Usar factory function (recomendado)
provider = create_provider("tess")

# Opção 2: Criar instância diretamente (menos recomendado)
provider = TessProvider()
```

### 2. Compatibilidade com Injeção de Dependência

#### Antes:

```python
def executa_comando(provider=None):
    # Criar provedor se não fornecido
    if provider is None:
        provider = TessProvider()
    
    # Usar o provedor...
```

#### Depois:

```python
from domain.interfaces import TessProviderInterface
from infrastructure.providers import create_provider

# Ao definir o parâmetro, use a interface do domínio
def executa_comando(provider: TessProviderInterface = None):
    # Criar provedor se não fornecido
    if provider is None:
        provider = create_provider("tess")
    
    # Usar o provedor...
```

### 3. Uso com Testes

#### Antes:

```python
# Mockar diretamente a classe
@mock.patch('src.providers.TessProvider')
def test_algo(mock_provider):
    # Configurar o mock...
```

#### Depois:

```python
# Opção 1: Mockar a interface (preferível)
class MockTessProvider(TessProviderInterface):
    # Implementar métodos necessários...

# No teste:
def test_algo():
    mock_provider = MockTessProvider()
    # Usar o mock...

# Opção 2: Mockar a factory
@mock.patch('infrastructure.providers.create_provider')
def test_algo(mock_create):
    mock_provider = mock.MagicMock(spec=TessProviderInterface)
    mock_create.return_value = mock_provider
    # Continuar o teste...
```

## Período de Transição

Para facilitar a migração, as classes em `src/providers` foram transformadas em adaptadores que:

1. Emitem avisos de depreciação
2. Delegam chamadas para as implementações em `infrastructure/providers`
3. Mantêm comportamento de fallback caso a implementação da infraestrutura não esteja disponível

Recomenda-se migrar o código gradualmente para usar diretamente as implementações da camada de infraestrutura. Os adaptadores em `src/providers` serão removidos em versões futuras.

### Cronograma de Depreciação

| Data | Fase |
|------|------|
| Atual | Versão 1.0: Aviso de depreciação |
| Versão 1.1 | Adicionar mais avisos e logging detalhado |
| Versão 2.0 | Remoção dos componentes em `src/providers` |

## Exemplos Completos

### Exemplo 1: Listar Agentes

#### Antes:

```python
from src.providers import TessProvider

def listar_agentes_disponiveis():
    provider = TessProvider()
    return provider.list_agents()
```

#### Depois:

```python
from infrastructure.providers import create_provider

def listar_agentes_disponiveis():
    provider = create_provider("tess")
    return provider.list_agents()
```

### Exemplo 2: Caso de Uso com Injeção de Dependência

#### Antes:

```python
from src.providers import TessProvider

class AgentUseCase:
    def __init__(self, provider=None):
        self.provider = provider or TessProvider()
    
    def execute_agent(self, agent_id, prompt):
        # Implementação...
```

#### Depois:

```python
from domain.interfaces import TessProviderInterface
from infrastructure.providers import create_provider

class AgentUseCase:
    def __init__(self, provider: TessProviderInterface = None):
        self.provider = provider or create_provider("tess")
    
    def execute_agent(self, agent_id, prompt):
        # Implementação...
```

## Perguntas Frequentes

### Q: Por que foi necessária esta mudança?

R: Para alinhar o código com os princípios de Clean Architecture e DDD, separando claramente as responsabilidades entre as camadas e facilitando testes e manutenção.

### Q: Preciso migrar todo o código de uma vez?

R: Não. A migração pode ser feita gradualmente, aproveitando o período de compatibilidade dos adaptadores em `src/providers`.

### Q: O que acontece se eu continuar usando as implementações antigas?

R: Por enquanto elas continuarão funcionando, mas emitirão avisos de depreciação. Em versões futuras, serão removidas.

### Q: Como criar um novo provedor?

R: 1. Defina uma interface no domínio; 2. Implemente a interface na camada de infraestrutura; 3. Registre o provedor na fábrica.

## Verificação de Conformidade

Para verificar se seu código está em conformidade com a nova arquitetura, execute:

```bash
python -m tools.testing.arch_test
```

Isso verificará se há padrões de importação não recomendados e violações de dependência entre camadas.

---

Para mais informações ou suporte na migração, consulte o documento `docs/arquitetura_referencia.md` ou entre em contato com a equipe de arquitetura. 