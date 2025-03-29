# Arquitetura de Referência - Projeto crew_ai_tess_pareto

## Visão Geral

Este documento estabelece a arquitetura de referência para o projeto `crew_ai_tess_pareto`,
alinhada com os princípios de Clean Architecture e Domain-Driven Design (DDD).
Serve como guia para refatoração e desenvolvimento de novos componentes.

## Princípios Arquiteturais

A arquitetura do projeto segue os seguintes princípios:

1. **Separação de Responsabilidades**: Cada componente tem uma responsabilidade única e claramente definida.
2. **Inversão de Dependência**: Camadas internas não dependem de camadas externas, apenas de abstrações.
3. **Independência de Frameworks**: O domínio não deve depender de frameworks ou bibliotecas externas.
4. **Testabilidade**: A arquitetura facilita a escrita de testes automatizados em todos os níveis.
5. **Design Explícito**: A estrutura do código deve refletir o domínio e ser compreensível para não-programadores.

## Estrutura em Camadas

A arquitetura é organizada em camadas concêntricas, onde as dependências fluem de fora para dentro:

![Diagrama de Camadas](https://miro.medium.com/max/720/1*0u-ekVHFu7Om7Z-VTwFHvg.png)

### 1. Camada de Domínio

A camada mais interna contém as entidades, regras de negócio, eventos, exceções e interfaces do domínio.

**Diretório**: `domain/`

**Responsabilidades**:
- Representar conceitos do negócio (entidades e objetos de valor)
- Implementar regras de negócio invariantes
- Definir interfaces para serviços externos
- Ser independente de frameworks e detalhes técnicos

**Componentes**:
- `domain/entities/`: Classes que representam conceitos centrais do negócio
- `domain/value_objects/`: Objetos imutáveis que representam conceitos sem identidade
- `domain/exceptions/`: Exceções específicas do domínio
- `domain/events/`: Eventos do domínio
- `domain/interfaces/`: Interfaces para serviços e repositórios
- `domain/services/`: Serviços do domínio (operações que não pertencem a uma entidade específica)

### 2. Camada de Aplicação

Contém os casos de uso da aplicação, orquestrando o fluxo de dados e regras de negócio.

**Diretório**: `application/`

**Responsabilidades**:
- Implementar casos de uso da aplicação
- Orquestrar entidades e serviços do domínio
- Gerenciar transações e coordenar fluxos
- Implementar lógica específica da aplicação

**Componentes**:
- `application/use_cases/`: Implementações dos casos de uso
- `application/services/`: Serviços da aplicação
- `application/dto/`: Objetos de transferência de dados
- `application/exceptions/`: Exceções específicas da aplicação
- `application/interfaces/`: Interfaces da camada de aplicação
- `application/factories/`: Fábricas para criar objetos complexos

### 3. Camada de Infraestrutura

Implementa as interfaces definidas no domínio, fornecendo adaptadores para serviços externos.

**Diretório**: `infrastructure/`

**Responsabilidades**:
- Implementar adaptadores para serviços externos
- Gerenciar persistência de dados
- Implementar comunicação com APIs externas
- Fornecer implementações técnicas para interfaces do domínio

**Componentes**:
- `infrastructure/repositories/`: Implementações de repositórios
- `infrastructure/providers/`: Provedores para APIs externas
- `infrastructure/persistence/`: Código relacionado à persistência
- `infrastructure/mcp_servers/`: Implementações de servidores MCP
- `infrastructure/adapters/`: Adaptadores para serviços externos

### 4. Camada de Interface

Contém os pontos de entrada para a aplicação, incluindo CLI, API e interfaces gráficas.

**Diretório**: `interfaces/`

**Responsabilidades**:
- Gerenciar entrada e saída do usuário
- Validar entrada do usuário
- Formatar saída para apresentação
- Gerenciar fluxo de controle de alto nível

**Componentes**:
- `interfaces/cli/`: Interface de linha de comando
- `interfaces/api/`: Interface de API (se aplicável)
- `interfaces/gui/`: Interface gráfica (se aplicável)
- `interfaces/controllers/`: Controladores para gerenciar requisições

## Ferramentas e Utilitários Centralizados

Componentes que fornecem funcionalidades compartilhadas para as diferentes camadas.

**Diretório**: `tools/`

**Responsabilidades**:
- Fornecer utilitários reusáveis
- Implementar ferramentas compartilhadas
- Centralizar integrações com ferramentas externas

**Componentes**:
- `tools/registry.py`: Registro centralizado de ferramentas
- `tools/mcpx_*.py`: Ferramentas relacionadas ao protocolo MCP
- `tools/tess_*.py`: Ferramentas relacionadas ao TESS

## Estrutura de Projeto Completa

```
crew_ai_tess_pareto/
│
├── domain/                  # Camada de Domínio
│   ├── entities/            # Entidades do domínio
│   ├── value_objects/       # Objetos de valor
│   ├── services/            # Serviços do domínio
│   ├── interfaces/          # Interfaces do domínio
│   ├── events/              # Eventos do domínio
│   └── exceptions/          # Exceções do domínio
│
├── application/             # Camada de Aplicação
│   ├── use_cases/           # Casos de uso
│   ├── services/            # Serviços da aplicação
│   ├── dto/                 # Objetos de transferência de dados
│   ├── interfaces/          # Interfaces da aplicação
│   ├── factories/           # Fábricas
│   └── exceptions/          # Exceções da aplicação
│
├── infrastructure/          # Camada de Infraestrutura
│   ├── repositories/        # Implementações de repositórios
│   ├── providers/           # Provedores para APIs externas
│   ├── persistence/         # Persistência de dados
│   ├── mcp_servers/         # Implementações de servidores MCP
│   └── adapters/            # Adaptadores para serviços externos
│
├── interfaces/              # Camada de Interface
│   ├── cli/                 # Interface de linha de comando
│   ├── api/                 # Interface de API (se aplicável)
│   └── controllers/         # Controladores
│
├── tools/                   # Ferramentas e Utilitários
│   ├── registry.py          # Registro centralizado
│   ├── mcpx_simple.py       # Cliente para o MCP
│   └── tess_nl_processor.py # Processador de linguagem natural
│
├── tests/                   # Testes Automatizados
│   ├── unit/                # Testes unitários
│   ├── integration/         # Testes de integração
│   └── e2e/                 # Testes de ponta a ponta
│
├── scripts/                 # Scripts utilitários
│   └── find_tools_usage.py  # Script para migração de ferramentas
│
├── docs/                    # Documentação
│   ├── arquitetura_referencia.md  # Este documento
│   └── guia_migracao_*.md          # Guias de migração
│
├── examples/                # Exemplos de uso
│   ├── tools/               # Exemplos de ferramentas
│   └── mcp/                 # Exemplos de servidores MCP
│
├── requirements.txt         # Dependências do projeto
└── README.md                # Documentação principal
```

## Fluxo de Controle

A figura abaixo ilustra o fluxo de controle típico através das camadas:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │    │                 │
│    Interface    │───▶│   Aplicação     │───▶│     Domínio     │◀───│ Infraestrutura  │
│    (CLI/API)    │    │  (Casos de Uso) │    │   (Entidades)   │    │  (Repositórios) │
│                 │◀───│                 │◀───│                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

1. A requisição começa na Interface
2. A Interface chama um Caso de Uso na camada de Aplicação
3. O Caso de Uso coordena Entidades e Serviços do Domínio
4. O Domínio usa interfaces implementadas pela Infraestrutura
5. O resultado flui de volta através das camadas

## Guias de Implementação

### Implementação de Um Novo Recurso

Para implementar um novo recurso, siga estes passos:

1. **Domínio**: Identifique e implemente entidades, regras e interfaces relacionadas
2. **Aplicação**: Implemente os casos de uso que orquestram o domínio
3. **Infraestrutura**: Implemente as interfaces definidas no domínio
4. **Interface**: Implemente os pontos de entrada para o usuário

### Padrões Recomendados

- **Injeção de Dependência**: Use construtores para fornecer dependências
- **Factory Method**: Para criar objetos complexos
- **Repository**: Para acesso a dados persistentes
- **Adapter**: Para integrar com sistemas externos
- **Registry**: Para centralizar acesso a implementações

## Componentes Específicos do Projeto

### Servidores MCP

Para implementar um novo servidor MCP:

1. Crie um adaptador que implemente a interface `MCPServerInterface`
2. Registre o adaptador no `MCPServerRegistry`
3. Implemente testes para validar a compatibilidade

### Ferramentas

Para adicionar uma nova ferramenta:

1. Implemente a funcionalidade em `tools/`
2. Registre a ferramenta no `ToolRegistry`
3. Documente o uso da ferramenta

## Testes

A estratégia de testes segue a estrutura em camadas:

- **Testes Unitários**: Testam componentes isolados
- **Testes de Integração**: Testam interação entre componentes
- **Testes E2E**: Testam fluxos completos

## Monitoramento de Conformidade Arquitetural

Para garantir a conformidade com esta arquitetura:

1. **Revisões de Código**: Verificar aderência aos princípios
2. **Linters Arquiteturais**: Usar ferramentas para validar dependências
3. **Documentação**: Manter documentação arquitetural atualizada

## Migração de Código Existente

Para migrar código existente para essa arquitetura:

1. Identifique a camada apropriada para cada componente
2. Refatore gradualmente, mantendo a compatibilidade
3. Siga os guias de migração específicos

## Conclusão

Esta arquitetura de referência estabelece um padrão unificado para o projeto `crew_ai_tess_pareto`,
promovendo princípios de Clean Architecture e DDD. Ela serve como guia para refatorações
e desenvolvimento de novos componentes, garantindo consistência arquitetural em todo o projeto.

---

**Versão**: 1.0
**Data**: [DATA_ATUAL] 