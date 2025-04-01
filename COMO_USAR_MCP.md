# Guia de Uso do Desktop Commander MCP

Este guia explica como utilizar o DesktopCommanderMCP para interagir com o sistema de arquivos e executar comandos no terminal através de ferramentas MCP (Model Context Protocol).


## O que é o Desktop Commander MCP?

O Desktop Commander MCP é uma ferramenta que permite que modelos de linguagem como o Claude possam:

- Executar comandos no terminal
- Gerenciar processos e sessões
- Ler e modificar arquivos com alta precisão
- Realizar buscas avançadas no código
- Manipular o sistema de arquivos

Foi desenvolvido para transformar o Claude em um assistente poderoso para desenvolvimento, automação e gerenciamento de projetos.

## Ferramentas Principais

O Desktop Commander disponibiliza várias ferramentas organizadas em categorias:

### Ferramentas de Terminal
- `execute_command`: Executar comandos no terminal
- `read_output`: Ler saída de comandos em execução
- `list_processes`: Listar processos em execução
- `kill_process`: Encerrar processos pelo PID
- `list_sessions`: Listar sessões de terminal ativas
- `force_terminate`: Forçar término de sessões

### Ferramentas de Sistema de Arquivos
- `read_file`: Ler conteúdo de arquivos
- `write_file`: Escrever/substituir arquivos
- `list_directory`: Listar conteúdo de diretórios
- `create_directory`: Criar diretórios
- `move_file`: Mover/renomear arquivos
- `get_file_info`: Obter informações de arquivos
- `search_files`: Buscar arquivos por nome

### Ferramentas de Código
- `search_code`: Buscar padrões em código (ripgrep)
- `edit_block`: Editar blocos específicos de código

## Comandos no Terminal

### Executar um comando simples
```
Por favor, execute o comando 'ls -la' para listar os arquivos no diretório atual.
```

### Executar um comando com timeout
```
Execute o comando 'npm install' com um timeout de 30 segundos.
```

### Listar processos em execução
```
Liste todos os processos Node.js em execução no sistema.
```

### Encerrar um processo
```
Por favor, encerre o processo com PID 1234.
```

## Manipulação de Arquivos

### Ler um arquivo
```
Mostre o conteúdo do arquivo package.json.
```

### Criar/Modificar um arquivo
```
Crie um arquivo chamado hello.js com o seguinte conteúdo:
console.log('Hello, world!');
```

### Edição cirúrgica de arquivos
```
No arquivo server.js, altere a porta de 3000 para 8080.
```

### Listar diretório
```
Liste os arquivos na pasta src.
```

### Criar diretório
```
Crie uma pasta chamada 'components' dentro da pasta 'src'.
```

## Busca de Código

### Busca simples por padrão
```
Busque por todas as ocorrências da string "useState" nos arquivos JavaScript.
```

### Busca avançada com contexto
```
Encontre todas as funções que contêm "async" em arquivos .ts, mostrando 3 linhas de contexto.
```

### Localizar arquivos específicos
```
Encontre todos os arquivos que contenham a palavra "component" no nome.
```

## Cenários de Uso Comuns

### 1. Explorar um projeto desconhecido
```
Pode me ajudar a entender a estrutura deste projeto? Comece listando os arquivos importantes e me diga para que serve cada um.
```

### 2. Refatorar um componente
```
Preciso refatorar este componente React para usar hooks. Pode me ajudar a identificar as alterações necessárias?
```

### 3. Debugar um problema
```
Estou com um erro no meu servidor Node. Pode verificar os logs e me ajudar a entender o que está acontecendo?
```

### 4. Automatizar tarefas repetitivas
```
Preciso renomear todas as instâncias de 'UserProfile' para 'Profile' em todos os arquivos. Pode me ajudar com isso?
```

## Solução de Problemas

### Permissões Insuficientes
Se o Claude indicar problemas de permissão:

1. Verifique se o Claude tem acesso ao diretório que você está tentando acessar
2. Os diretórios permitidos são mostrados por `list_allowed_directories`
3. Se necessário, ajuste as permissões do diretório ou mova o projeto para um diretório com acesso

### Comandos Não Executados
Se os comandos não estiverem sendo executados:

1. Verifique se o comando está na lista de bloqueados com `list_blocked_commands`
2. Certifique-se de que o Node.js tem permissão para executar o comando
3. Tente executar comandos mais simples primeiro para confirmar que o MCP está funcionando

### Comandos Longos
Para comandos que demoram mais de 5 segundos:

1. O Claude receberá apenas a saída inicial
2. Use `read_output` com o PID para obter atualizações
3. Se necessário, use `force_terminate` para interromper o comando

## Dicas e Boas Práticas

### Para melhor desempenho

1. **Seja específico em suas solicitações**: Em vez de "mostre-me os arquivos", diga "liste os arquivos na pasta src/components".

2. **Use o contexto adequado**: Se estiver trabalhando em um arquivo específico, mencione-o para que o Claude não precise solicitar essa informação.

3. **Para edições complexas**: Descreva claramente as alterações que deseja fazer e forneça exemplos quando possível.

4. **Para busca de código**: Especifique o tipo de arquivo, o padrão a ser buscado e a quantidade de contexto necessária.

5. **Tenha paciência com comandos longos**: Comandos como instalações de pacotes podem levar tempo. O Claude informará o PID para que você possa verificar a saída posteriormente.

6. **Verifique as alterações**: Sempre verifique o resultado das edições de arquivo antes de continuar.

7. **Permita que o Claude aprenda**: Se ele fizer algo de forma incorreta, explique como você prefere que seja feito.

