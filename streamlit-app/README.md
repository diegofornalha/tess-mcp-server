# Interface Streamlit para TESS-MCP

Esta é uma interface gráfica baseada em Streamlit para interagir com o servidor TESS-MCP, permitindo acessar e executar ferramentas TESS através do protocolo MCP.

## Funcionalidades

- **Exploração de Ferramentas**: Liste e execute todas as ferramentas disponíveis no servidor TESS-MCP.
- **Exploração de Agentes**: Descubra, visualize detalhes e execute agentes TESS.
- **Histórico de Execuções**: Mantenha um registro de todas as execuções realizadas durante a sessão.
- **Suporte a WebSocket**: Compatível com todas as funcionalidades do servidor TESS-MCP, incluindo notificações em tempo real.

## Requisitos

- Python 3.8 ou superior
- Servidor TESS-MCP rodando na porta 3001

## Instalação

1. Clone este repositório
2. Navegue até a pasta da aplicação Streamlit:
   ```bash
   cd mcp-server-tess-xtp/streamlit-app
   ```
3. Execute o script de inicialização:
   ```bash
   ./run.sh
   ```

O script irá:
- Criar um ambiente virtual Python
- Instalar todas as dependências necessárias
- Iniciar a aplicação Streamlit

## Uso

Após iniciar a aplicação, acesse:

```
http://localhost:8501
```

### Abas Disponíveis

1. **Executar Ferramentas**: Selecione e execute qualquer ferramenta TESS disponível.
2. **Explorar Agentes**: Visualize a lista de agentes disponíveis, seus detalhes e execute-os.
3. **Histórico**: Consulte todas as execuções realizadas na sessão atual.

## Configuração

O servidor TESS-MCP é configurado por padrão para o endereço `http://localhost:3001`. Se o servidor estiver em outro endereço, edite a variável `TESS_MCP_URL` no arquivo `app.py`.

## Solução de Problemas

- **Erro de Conexão**: Verifique se o servidor TESS-MCP está em execução na porta 3001.
- **Erro de Dependências**: Execute novamente o script `run.sh` para garantir que todas as dependências estejam instaladas.
- **Erros nas Chamadas de API**: Consulte os logs do servidor TESS-MCP para mais detalhes sobre erros específicos.

## Licença

Este projeto está licenciado sob a Licença MIT. 