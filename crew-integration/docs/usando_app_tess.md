# Guia de Uso - Gerador de Anúncios TESS API

Este guia explica como utilizar a aplicação Streamlit para gerar anúncios para Google Ads através da API TESS.

## Requisitos

- Python 3.6 ou superior
- Bibliotecas: streamlit, pandas, requests, dotenv
- Chave de API TESS válida

## Iniciando a Aplicação

Para iniciar a aplicação, execute o script `start_app_tess.sh` no terminal:

```bash
cd mcp-server-tess-xtp/crew-integration
./start_app_tess.sh
```

A aplicação abrirá automaticamente no seu navegador padrão. Se não abrir, acesse o endereço mostrado no terminal (geralmente http://localhost:8501).

## Navegação

A aplicação está organizada em quatro seções principais, acessíveis pelo menu na barra lateral esquerda:

1. **Listar Agentes**: Visualize todos os agentes TESS disponíveis.
2. **Gerar Anúncios**: Interface principal para criação de anúncios.
3. **Modelos Disponíveis**: Consulte os modelos de linguagem disponíveis.
4. **Configurações**: Gerenciamento de configurações da API.

## Listar Agentes

Esta seção permite visualizar todos os agentes disponíveis na API TESS.

1. Clique no botão "Atualizar Lista de Agentes" para carregar os agentes disponíveis.
2. A lista será exibida em formato de tabela com ID, Descrição e Categoria.
3. Os agentes carregados aqui estarão disponíveis para seleção na seção "Gerar Anúncios".

> **Dica**: A API TESS mostra apenas os agentes acessíveis com sua chave API atual. Se não vir todos os agentes esperados, verifique suas permissões.

## Gerar Anúncios

Esta é a seção principal para criação de anúncios:

1. **Seleção do Agente**:
   - Selecione o agente desejado no menu suspenso (mostra ID e descrição).
   - O ID 45 é recomendado para anúncios de Google Ads.
   - Quando um agente é selecionado, o sistema automaticamente consulta seus parâmetros usando o CLI (python scripts/tess_api_cli.py info [ID])
   - A aplicação mostrará quais campos adicionais são necessários para aquele agente específico.

2. **Interface de Chat com TESS**:
   - Um assistente conversacional permite enviar todas as informações de uma vez.
   - Você pode enviar as informações em formato estruturado:
   
     ```
     Nome da empresa: [nome]
     Descrição: [descrição do negócio] 
     Diferenciais: [lista de diferenciais]
     Call to action: [chamada para ação]
     [Campos adicionais específicos do agente]
     ```
   
   - Para agentes especiais (como o 76), campos adicionais como "topico" serão solicitados automaticamente.
   - O assistente mostrará quais informações foram capturadas e o que ainda falta.

3. **Campos Adicionais**:
   - Após fornecer as informações básicas, campos específicos do agente aparecerão como formulário.
   - Estes campos são detectados automaticamente a partir da consulta CLI ou API.
   - É necessário preencher todos os campos obrigatórios antes de gerar os anúncios.

4. **Configurações**:
   - Após completar o chat, você poderá configurar os parâmetros técnicos:
   - **Temperatura**: Ajuste o nível de criatividade (0.0-1.0).
   - **Tamanho máximo**: Defina o tamanho máximo para os anúncios.
   - **Modelo**: Selecione o modelo de linguagem (GPT-4o recomendado).
   - **Idioma**: Escolha o idioma desejado para os anúncios.

5. **Geração e Visualização**:
   - Clique em "Gerar Anúncios" para processar as informações.
   - Use "Limpar e Recomeçar" se quiser iniciar uma nova conversa.
   - Os anúncios serão exibidos em formato estruturado com títulos e descrições.
   - Clique em "Exportar como Markdown" para baixar os resultados em formato .md.
   - Use o expandidor "Ver resposta completa da API" para visualizar detalhes técnicos.

> **Dica para Melhores Resultados**:
> - Forneça todas as informações de uma vez no formato estruturado sugerido.
> - Seja específico na descrição do negócio e diferenciais.
> - Para agentes especiais (como 76 para roteiros de lives), forneça informações específicas como "topico", "seu-instagram" e "objetivo".
> - Se ocorrer algum erro, verifique os detalhes técnicos expandindo a seção correspondente.

## Modelos Disponíveis

Esta seção permite consultar todos os modelos de linguagem disponíveis para um agente específico:

1. Insira o ID do agente que deseja consultar (padrão: 45).
2. Clique em "Listar Modelos" para visualizar os modelos disponíveis.
3. A lista mostrará primeiro os modelos recomendados e depois todos os modelos disponíveis.

> **Dica**: GPT-4o é o modelo recomendado para a maioria dos casos, com melhor compatibilidade e resultados.

## Configurações

Na seção de configurações, você pode:

1. **Gerenciar sua Chave API TESS**:
   - Visualize ou atualize sua chave de API (parcialmente mascarada por segurança).

2. **Configurar Formato de Saída**:
   - Escolha entre saída formatada, JSON ou texto puro para os resultados.

3. Clique em "Salvar Configurações" para aplicar as mudanças.

## Solução de Problemas Comuns

### Erros 422 (Unprocessable Entity)

Este erro ocorre quando:
- Parâmetros obrigatórios estão faltando
- O valor de `model` não é válido
- O formato de um parâmetro está incorreto

**Solução**: Verifique se todos os campos estão preenchidos e use a seção "Modelos Disponíveis" para confirmar modelos válidos.

### Erro 401 (Unauthorized)

Este erro ocorre quando a chave de API é inválida ou expirou.

**Solução**: Atualize sua chave de API na seção "Configurações".

### Anúncios de Baixa Qualidade

Se os anúncios gerados não atenderem às expectativas:

1. Melhore a descrição da empresa - seja mais específico e detalhado.
2. Forneça diferenciais mais concretos e mensuráveis.
3. Experimente diferentes temperaturas: 0.5-0.6 para mais conservador, 0.8-0.9 para mais criativo.
4. Teste diferentes modelos na seção "Modelos Disponíveis".

## Usos Recomendados

A aplicação é ideal para:

1. **Marketing Digital**: Criação rápida de anúncios para Google Ads.
2. **Agências**: Geração de múltiplas variações para testes A/B.
3. **Pequenas Empresas**: Criação de anúncios profissionais sem expertise em publicidade.
4. **E-commerce**: Anúncios para produtos e campanhas promocionais. 