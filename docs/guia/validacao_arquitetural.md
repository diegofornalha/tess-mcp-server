# Guia de Validação Arquitetural

Este documento descreve o sistema de validação arquitetural implementado para garantir que o código do projeto siga os princípios da Arquitetura Limpa (Clean Architecture) e do Desenvolvimento Orientado a Domínio (DDD).

## Objetivo

O objetivo da validação arquitetural é:
- Garantir que as dependências entre as camadas sigam o fluxo correto
- Prevenir importações que violem os princípios de arquitetura limpa
- Manter a camada de domínio isolada e independente
- Facilitar a manutenção e evolução do código a longo prazo

## Componentes Implementados

### 1. Checker para Pylint (`tools/linting/architecture_checker.py`)

Este componente é um plugin para o Pylint que verifica as importações no código-fonte e identifica violações das regras arquiteturais:

- **Características principais:**
  - Verifica cada importação para determinar sua origem e destino em termos de camadas
  - Emite avisos específicos para importações que violam a arquitetura
  - Configurável através do arquivo `.pylintrc`

- **Regras implementadas:**
  - A camada de domínio não deve importar das outras camadas
  - A camada de aplicação só deve importar da camada de domínio
  - A camada de infraestrutura só deve importar das camadas de domínio e aplicação
  - A camada de interface só deve importar das camadas inferiores

### 2. Testes de Arquitetura (`tools/testing/arch_test.py`)

Este componente contém testes automatizados que verificam se o código-fonte segue as regras arquiteturais:

- **Funcionalidades:**
  - Extrai todas as importações dos arquivos Python
  - Determina a camada à qual cada arquivo pertence
  - Verifica se as importações seguem as regras arquiteturais
  - Identifica e reporta violações

- **Testes implementados:**
  - `test_domain_doesnt_import_other_layers`: Garante que a camada de domínio não importa das outras camadas
  - `test_application_imports`: Verifica que a camada de aplicação só importa da camada de domínio
  - `test_infrastructure_imports`: Verifica que a camada de infraestrutura só importa das camadas de domínio e aplicação
  - `test_interfaces_imports`: Verifica que a camada de interfaces só importa das camadas inferiores

### 3. Testes Unitários de Arquitetura (`tests/unit/architecture/test_dependency_rules.py`)

Este conjunto de testes valida especificamente as regras de dependência entre camadas:

- **Funcionalidades:**
  - Verifica se os provedores implementam as interfaces definidas no domínio
  - Garante que as entidades permanecem na camada de domínio
  - Verifica a correta implementação das interfaces
  - Confirma que não há dependências cíclicas

## Como Executar a Validação Arquitetural

### Verificação com Pylint

```bash
# Verificar todo o projeto
pylint --load-plugins=tools.linting.architecture_checker .

# Verificar um arquivo específico
pylint --load-plugins=tools.linting.architecture_checker caminho/para/arquivo.py

# Verificar apenas problemas arquiteturais
pylint --load-plugins=tools.linting.architecture_checker --disable=all --enable=architectural-dependency-violation .
```

### Executar Testes de Arquitetura

```bash
# Executar testes de arquitetura
python -m tools.testing.arch_test

# Executar com detalhes
python -m tools.testing.arch_test --verbose
```

### Executar Testes Unitários de Dependências

```bash
# Executar testes unitários de arquitetura
pytest tests/unit/architecture/test_dependency_rules.py -v
```

## Exceções às Regras

Em alguns casos, podem existir exceções legítimas às regras arquiteturais. Estas exceções podem ser configuradas no arquivo `.pylintrc` na seção `[ARCHITECTURE]`:

```
[ARCHITECTURE]
architecture-allowed-imports=
    domain.interfaces:domain.exceptions,
    domain:pytest  # Permitido para testes dentro da camada de domínio
```

## Resolução de Problemas Comuns

### 1. Violações nas Camadas

Se você encontrar um erro como `domain-imports-outer-layer` ou similar, você precisa:

1. Identificar a importação problemática
2. Verificar se essa importação é realmente necessária
3. Refatorar o código para seguir as regras arquiteturais:
   - Mover a lógica compartilhada para a camada de domínio
   - Criar uma interface no domínio e implementações nas camadas externas
   - Aplicar injeção de dependência

### 2. Falsas Violações

Se você acredita que uma violação é um falso positivo:

1. Verifique se a estrutura do diretório reflete corretamente a camada à qual o código pertence
2. Se a importação for legítima, adicione-a à lista de exceções no `.pylintrc`
3. Documente por que a exceção é necessária

## Integração Contínua

Para garantir que as regras arquiteturais sejam seguidas consistentemente, os testes de arquitetura devem ser executados como parte do processo de CI:

```yaml
# Exemplo de configuração para CI
architecture-validation:
  script:
    - pylint --load-plugins=tools.linting.architecture_checker --disable=all --enable=architectural-dependency-violation .
    - python -m tools.testing.arch_test
    - pytest tests/unit/architecture/test_dependency_rules.py -v
```

## Conclusão

A validação arquitetural automatizada ajuda a manter a integridade da arquitetura do projeto ao longo do tempo. Ao detectar violações precocemente, podemos garantir que o código continue seguindo os princípios de Clean Architecture e DDD, facilitando a manutenção e evolução do sistema. 