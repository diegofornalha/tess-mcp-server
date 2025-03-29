"""
Ferramentas utilizadas pelos agentes

Este pacote fornece ferramentas unificadas para o projeto crew_ai_tess_pareto,
resolvendo a duplicação entre os diretórios 'src/tools' e 'tools'.

Para utilizar as ferramentas, importe através do registro centralizado:

```python
from tools.registry import get_mcp_client, get_nl_processor

# Cria cliente MCP
client = get_mcp_client(session_id="sua-sessao")

# Processa comandos em linguagem natural
processor = get_nl_processor()
```

Ou utilize o ToolRegistry diretamente:

```python
from tools.registry import ToolRegistry

# Lista todas as ferramentas disponíveis
ferramentas = ToolRegistry.list()

# Cria instância de uma ferramenta específica
client = ToolRegistry.factory("mcp_client", session_id="sua-sessao")
```
"""

# Importar símbolos públicos do módulo registry
from .registry import (
    ToolRegistry,
    MCPRunClient,
    TessNLProcessor,
    get_mcprun_tools,
    get_mcp_client,
    get_nl_processor
)

# Exportar símbolos públicos
__all__ = [
    # Classes principais
    "ToolRegistry",
    
    # Implementações recomendadas
    "MCPRunClient",
    "TessNLProcessor",
    "get_mcprun_tools",
    
    # Funções auxiliares
    "get_mcp_client",
    "get_nl_processor",
] 