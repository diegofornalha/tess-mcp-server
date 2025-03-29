# Guia de Migração: Ferramentas Centralizadas

Este documento fornece instruções para migrar código existente que utiliza ferramentas duplicadas entre `src/tools` e `tools/` para o novo registro centralizado de ferramentas.

## Contexto

Identificamos uma inconsistência arquitetural crítica no projeto `crew_ai_tess_pareto`: 
a duplicação de funcionalidades entre os diretórios `src/tools` e `tools/`. 
Esta duplicação resultava em confusão sobre qual implementação usar, 
divergência de comportamentos e dificuldades na manutenção.

O novo registro centralizado (`tools/registry.py`) resolve este problema fornecendo:

1. Um ponto único para acesso a todas as ferramentas do projeto
2. Compatibilidade com código existente através da camada de depreciação
3. Nomenclatura padronizada e metadados para ferramentas
4. Processo de migração gradual, sem quebrar código existente

## Como Migrar

### 1. Importações

#### Antes:

```python
# Código antigo usando implementações de src/tools
from src.tools.mcpx_simple import MCPRunClient
from src.tools.mcp_nl_processor import MCPNLProcessor

# OU

# Código antigo usando implementações de tools/
from tools.mcpx_simple import MCPRunClient
from tools.tess_nl_processor import TessNLProcessor
```

#### Depois:

```python
# Código novo usando o registro centralizado
from tools.registry import get_mcp_client, get_nl_processor

# OU

from tools.registry import ToolRegistry
```

### 2. Criação de Instâncias

#### Antes:

```python
# Código antigo
client = MCPRunClient(session_id="minha-sessao")
processor = TessNLProcessor()
```

#### Depois:

```python
# Código novo usando funções auxiliares
client = get_mcp_client(session_id="minha-sessao")
processor = get_nl_processor()

# OU

# Código novo usando o factory pattern
client = ToolRegistry.factory("mcp_client", session_id="minha-sessao")
processor = ToolRegistry.factory("nl_processor")
```

### 3. Ferramentas Disponíveis

Para descobrir quais ferramentas estão disponíveis no registro:

```python
from tools.registry import ToolRegistry

# Listar todas as ferramentas (recomendadas e depreciadas)
todas_ferramentas = ToolRegistry.list(include_deprecated=True)

# Listar apenas ferramentas recomendadas
ferramentas_recomendadas = ToolRegistry.list()

# Imprimir ferramentas disponíveis
for nome, metadata in ferramentas_recomendadas.items():
    print(f"{nome}: {metadata['description']}")
```

## Mapeamento de Ferramentas

A tabela abaixo mapeia as implementações antigas para as novas ferramentas no registro centralizado:

| Implementação Antiga | Nova Ferramenta (Registry) | Status |
|----------------------|----------------------------|--------|
| `src.tools.mcpx_simple.MCPRunClient` | `tools.registry.get_mcp_client()` | ✅ Recomendada |
| `tools.mcpx_simple.MCPRunClient` | `tools.registry.get_mcp_client()` | ✅ Recomendada |
| `src.tools.mcp_nl_processor.MCPNLProcessor` | `tools.registry.get_nl_processor()` | ⚠️ Depreciada |
| `tools.tess_nl_processor.TessNLProcessor` | `tools.registry.get_nl_processor()` | ✅ Recomendada |
| `tools.mcpx_tools.get_mcprun_tools` | `tools.registry.get_mcprun_tools` | ✅ Recomendada |

## Compatibilidade com Versões Anteriores

Para garantir a compatibilidade com código existente, as ferramentas depreciadas continuarão funcionando, mas emitirão avisos de depreciação:

```python
import warnings

# Configurar para que os avisos sempre sejam exibidos
warnings.filterwarnings("always", category=DeprecationWarning)

# Usar ferramenta depreciada (emitirá aviso)
ferramenta_antiga = ToolRegistry.get("mcp_client_legacy")
```

## Exemplo Completo

Um exemplo prático de utilização do novo registro de ferramentas está disponível em:

```
examples/tools/exemplo_tools_registry.py
```

Este exemplo demonstra:
- Listagem de ferramentas disponíveis
- Uso do cliente MCP
- Uso do processador de linguagem natural
- Tratamento de ferramentas depreciadas

## Boas Práticas

1. **Sempre use o registro centralizado** em vez de importações diretas
2. **Prefira as ferramentas recomendadas** em vez das depreciadas
3. **Use funções auxiliares** para instanciar ferramentas comuns
4. **Atualize código existente gradualmente** para usar o novo registro

## Próximos Passos para Desenvolvedores

1. Identifique e migre todas as instâncias de uso direto das ferramentas duplicadas
2. Contribua com melhorias para o registro centralizado
3. Reporte problemas ou sugestões para a equipe de arquitetura

## Timeline para Depreciação

- **Fase atual**: Coexistência entre implementações antigas e novas
- **Próxima fase** (3 meses): Avisos de depreciação mais rigorosos
- **Fase final** (6 meses): Remoção de implementações depreciadas

## Suporte

Para dúvidas ou suporte na migração, entre em contato com a equipe de arquitetura do projeto.

---

**Data de Atualização**: [DATA_ATUAL]
**Versão do Documento**: 1.0 