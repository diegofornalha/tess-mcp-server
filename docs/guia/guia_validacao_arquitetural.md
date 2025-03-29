# Guia de Validação Arquitetural Automatizada

Este documento descreve as estratégias e ferramentas para validação automatizada da conformidade arquitetural do projeto `crew_ai_tess_pareto`, garantindo a consistência com os princípios estabelecidos no documento de arquitetura de referência.

## Visão Geral

A validação arquitetural automatizada é fundamental para:

1. **Prevenir Regressões**: Evitar que mudanças violem a arquitetura definida
2. **Guiar Desenvolvedores**: Fornecer feedback imediato sobre violações
3. **Manter Consistência**: Garantir que todo o código siga os padrões estabelecidos
4. **Documentar Dependências**: Tornar explícitas as relações entre componentes

## Ferramentas Recomendadas

### 1. Pylint com Checkers Customizados

O Pylint pode ser estendido com checkers customizados para verificar regras específicas da arquitetura:

```python
# tools/linting/architecture_checker.py
from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from astroid import nodes

class ArchitectureChecker(BaseChecker):
    __implements__ = IAstroidChecker
    
    name = 'architecture'
    priority = -1
    msgs = {
        'E9001': (
            'Domain should not import from infrastructure',
            'domain-imports-infrastructure',
            'Domain layer should not depend on infrastructure layer'
        ),
        'E9002': (
            'Domain should not import from interface',
            'domain-imports-interface',
            'Domain layer should not depend on interface layer'
        ),
        # Outras mensagens...
    }
    
    def visit_import(self, node):
        # Verificar se estamos em um módulo do domínio
        if 'domain' in self.linter.current_file:
            for name in node.names:
                if name[0].startswith('infrastructure') or name[0].startswith('interfaces'):
                    self.add_message('domain-imports-infrastructure', node=node)
```

Configurar no arquivo `.pylintrc`:

```ini
[MASTER]
load-plugins=tools.linting.architecture_checker
```

### 2. Pytest Plugin para Verificação de Dependências

Criação de um plugin para Pytest que verifica as dependências entre camadas:

```python
# tools/testing/arch_test.py
import pytest
import ast
import os

def get_imports(file_path):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append(name.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for name in node.names:
                    imports.append(f"{node.module}.{name.name}")
    
    return imports

def test_domain_doesnt_import_infrastructure():
    domain_dir = 'domain'
    for root, _, files in os.walk(domain_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                imports = get_imports(file_path)
                
                for imp in imports:
                    assert not imp.startswith('infrastructure'), \
                        f"{file_path} imports from infrastructure: {imp}"
                    assert not imp.startswith('interfaces'), \
                        f"{file_path} imports from interfaces: {imp}"
```

### 3. Ferramenta Personalizada de Análise de Dependências

Um script que gera relatórios de dependências entre camadas:

```python
# tools/arch_analysis.py
import os
import ast
import graphviz
import networkx as nx

def build_dependency_graph(root_dir='.'):
    G = nx.DiGraph()
    
    for dir_path, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(dir_path, file)
                module_name = os.path.relpath(file_path, root_dir).replace('/', '.').replace('.py', '')
                
                # Adicionar nó para o módulo
                layer = get_layer(module_name)
                G.add_node(module_name, layer=layer)
                
                # Analisar importações
                imports = get_imports(file_path)
                for imp in imports:
                    if is_project_module(imp):
                        G.add_edge(module_name, imp)
    
    return G

def get_layer(module_name):
    if module_name.startswith('domain'):
        return 'domain'
    elif module_name.startswith('application'):
        return 'application'
    elif module_name.startswith('infrastructure'):
        return 'infrastructure'
    elif module_name.startswith('interfaces'):
        return 'interfaces'
    else:
        return 'other'

def visualize_dependencies(G):
    dot = graphviz.Digraph(comment='Project Dependencies')
    
    # Definir subgraphs para cada camada
    with dot.subgraph(name='cluster_domain') as c:
        c.attr(label='Domain Layer')
        for node in G.nodes():
            if G.nodes[node]['layer'] == 'domain':
                c.node(node)
    
    # Outras camadas...
    
    # Adicionar arestas
    for u, v in G.edges():
        dot.edge(u, v)
    
    dot.render('dependency_graph.gv', view=True)

def check_architecture_rules(G):
    violations = []
    
    for u, v in G.edges():
        u_layer = G.nodes[u]['layer']
        v_layer = G.nodes[v]['layer']
        
        # Regra: Domain não pode depender de outras camadas
        if u_layer == 'domain' and v_layer in ['application', 'infrastructure', 'interfaces']:
            violations.append(f"Violation: {u} ({u_layer}) depends on {v} ({v_layer})")
        
        # Regra: Application pode depender de domain, mas não de infrastructure ou interfaces
        if u_layer == 'application' and v_layer in ['infrastructure', 'interfaces']:
            violations.append(f"Violation: {u} ({u_layer}) depends on {v} ({v_layer})")
        
        # Regra: Infrastructure pode depender de domain, application, mas não de interfaces
        if u_layer == 'infrastructure' and v_layer in ['interfaces']:
            violations.append(f"Violation: {u} ({u_layer}) depends on {v} ({v_layer})")
    
    return violations

if __name__ == "__main__":
    G = build_dependency_graph()
    violations = check_architecture_rules(G)
    
    if violations:
        print("Architecture violations found:")
        for v in violations:
            print(f"- {v}")
        exit(1)
    else:
        print("No architecture violations found!")
        visualize_dependencies(G)
```

## Configuração do CI/CD

Integrar a validação arquitetural no pipeline CI/CD:

```yaml
# .github/workflows/arch-validation.yml
name: Architecture Validation

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pylint pytest networkx graphviz
    
    - name: Run architecture checks
      run: |
        pylint domain application infrastructure interfaces
        python -m pytest tools/testing/arch_test.py -v
        python tools/arch_analysis.py
```

## Integração com Editores

### VSCode

Configuração para VSCode:

```json
// .vscode/settings.json
{
  "python.linting.pylintEnabled": true,
  "python.linting.enabled": true,
  "python.linting.pylintArgs": [
    "--load-plugins=tools.linting.architecture_checker"
  ]
}
```

### PyCharm

Para PyCharm, configurar o Pylint como External Tool e adicionar o plugin customizado.

## Estratégia de Implementação

### Fase 1: Configuração Básica

1. **Implementar Pylint Checker**:
   - Criar checker para verificar importações inválidas
   - Configurar regras básicas de dependência entre camadas

2. **Configurar Pytest para Testes de Arquitetura**:
   - Implementar testes simples para verificar violações críticas
   - Integrar com a suite de testes existente

### Fase 2: Análise Detalhada

1. **Implementar Ferramenta de Análise de Dependências**:
   - Desenvolver script para gerar gráfico de dependências
   - Adicionar relatórios detalhados de violações

2. **Configurar Dashboard de Métricas**:
   - Quantificar violações por camada
   - Acompanhar progresso ao longo do tempo

### Fase 3: Integração Contínua

1. **Configurar CI/CD**:
   - Integrar validação no pipeline
   - Bloquear merges que introduzem violações

2. **Feedback em Tempo Real**:
   - Integrar com editores para feedback imediato
   - Desenvolver extensões para apresentar sugestões de correção

## Regras Arquiteturais a Verificar

1. **Regras de Dependência**:
   - Domínio não depende de nenhuma outra camada
   - Aplicação depende apenas do domínio
   - Infraestrutura depende do domínio e, potencialmente, da aplicação
   - Interface depende da aplicação e, potencialmente, do domínio

2. **Regras de Nomenclatura**:
   - Classes seguem convenções por camada (ex: entidades terminam com Entity)
   - Pacotes seguem estrutura definida na arquitetura de referência

3. **Regras de Organização**:
   - Implementações estão nas camadas corretas
   - Interfaces estão definidas antes das implementações

## Métricas de Conformidade

Métricas para acompanhar a conformidade arquitetural:

1. **Violations Ratio**: Número de violações / número total de importações
2. **Layer Coverage**: Porcentagem de código em cada camada
3. **Architecture Debt**: Número de violações ponderadas por severidade
4. **Migration Progress**: Redução no número de violações ao longo do tempo

## Exemplo de Relatório

```
======================= Architecture Validation Report =======================
Violations by Layer:
- Domain: 0 violations (0.0%)
- Application: 2 violations (5.3%)
- Infrastructure: 1 violation (0.8%)
- Interfaces: 0 violations (0.0%)

Total: 3 violations (1.2% of all dependencies)

Details:
- application/use_cases/agent_use_case.py imports from infrastructure.providers
- application/services/chat_service.py imports from interfaces.formatters
- infrastructure/adapters/tess_adapter.py imports from interfaces.cli

Improvement since last check: -2 violations (5 -> 3)

Architecture compliance score: 98.8% (target: 100%)
```

## Próximos Passos

1. Implementar o checker Pylint customizado
2. Configurar testes básicos de arquitetura
3. Gerar primeiro mapa de dependências
4. Integrar com CI/CD 