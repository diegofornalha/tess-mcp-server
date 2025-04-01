# Guia de Uso - Filtro de Agentes TESS

Este guia explica como utilizar a aplicação Streamlit para filtrar e visualizar agentes disponíveis na API TESS por tipo de IA.

## Iniciando a Aplicação

Para iniciar a aplicação, execute o script `start_filtro_agentes.sh` no terminal:

```bash
cd mcp-server-tess-xtp/crew-integration
chmod +x start_filtro_agentes.sh
./start_filtro_agentes.sh
```

A aplicação abrirá automaticamente no seu navegador padrão. Se não abrir, acesse o endereço mostrado no terminal (geralmente http://localhost:8501).

## Funcionalidades Principais

### Filtros por Tipo de IA

No menu lateral esquerdo, você encontrará as opções de filtro por tipo de IA:

- **Todos**: Exibe todos os agentes disponíveis
- **Imagem**: Agentes especializados em geração ou análise de imagens
- **Texto**: Agentes para geração de textos, incluindo anúncios
- **Chat**: Agentes conversacionais
- **Dublagem**: Agentes de áudio, narração ou dublagem
- **Código**: Agentes para geração ou análise de código
- **Vídeo**: Agentes relacionados a vídeos

Cada tipo de IA é representado por uma cor específica no card do agente para facilitar a identificação visual.

### Busca por Texto

Também no menu lateral, há um campo de busca onde você pode filtrar agentes por:
- ID
- Nome
- Descrição
- Categoria

Basta digitar o termo que deseja encontrar e os resultados serão filtrados automaticamente.

### Visualização dos Agentes

Os agentes são exibidos em cards organizados em uma grade de três colunas, contendo:
- Tipo de IA (com cor específica)
- ID do agente
- Nome
- Descrição
- Categoria
- Botão "Usar Agente"

### Ações Disponíveis

- **Atualizar Lista de Agentes**: Botão na barra lateral para recarregar a lista de agentes da API
- **Usar Agente**: Link em cada card que leva ao app_tess.py com o agente pré-selecionado

## Recursos Adicionais

- **Contagem de Resultados**: A aplicação mostra quantos agentes foram encontrados com os filtros atuais
- **Mensagem de Alerta**: Quando nenhum agente é encontrado, uma mensagem é exibida

## Solução de Problemas

### Erro de Conexão com a API

Se a aplicação exibir erros de conexão com a API TESS:
1. Verifique se sua chave de API está configurada corretamente no arquivo `.env`
2. Confirme que você tem acesso à API TESS
3. Verifique sua conexão com a internet

### Sem Agentes Visíveis

Se nenhum agente for exibido mesmo sem filtros:
1. Clique em "Atualizar Lista de Agentes"
2. Verifique se sua conta tem acesso a agentes na API TESS

## Integração com o App TESS

Este aplicativo de filtro está integrado ao app_tess.py. Ao clicar em "Usar Agente" em qualquer card:
1. Você será redirecionado para o aplicativo principal
2. O agente selecionado será pré-carregado
3. Você poderá prosseguir imediatamente para a geração de conteúdo 