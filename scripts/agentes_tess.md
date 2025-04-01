# Agentes TESS Disponíveis

Este documento lista todos os agentes disponíveis na API TESS organizados em páginas para fácil visualização.

## Página 1

| ID | Nome | Descrição | Categoria |
|----|------|-----------|-----------|
| 45 | Anúncios Google Ads | Use a Tess AI para criar anúncios incríveis para suas campanhas da marca no Google | Marketing/Google Ads |
| 48 | Anúncios de Produtos | Crie anúncios incríveis para suas campanhas de produtos ou serviços no Google Ads | Marketing/Google Ads |
| 49 | Anúncios Performance Max | Crie anúncios incríveis para suas campanhas de Performance Max no Google Ads | Marketing/Google Ads |
| 51 | Títulos de E-mail | Com a Tess AI, crie títulos audaciosos para maximizar a taxa de abertura de e-mails | Marketing/Email |
| 52 | Títulos E-mail (Lançamento) | Deixe a Tess AI criar títulos incríveis de email para seu lançamento de novas features | Marketing/Email |
| 53 | E-mails de Venda | Use a Tess IA para escrever os melhores e-mails de venda | Marketing/Email |
| 55 | E-mail de Feedback | Escreva um e-mail para encorajar seu cliente a deixar um feedback e comprar produtos similares | Marketing/Email |
| 59 | Plano Palavras-chave (Marca) | Crie um plano de palavras-chave a sua marca no Google Ads | Marketing/SEO |
| 60 | Plano Palavras-chave (Campanha) | Crie um plano de palavras-chave para campanha no Google Ads | Marketing/SEO |
| 67 | Posts para LinkedIn | Use a Tess para criar posts incríveis para seu LinkedIn | Marketing/Social Media |

## Página 2

| ID | Nome | Descrição | Categoria |
|----|------|-----------|-----------|
| 68 | Ideias para YouTube Ads | Crie uma lista de ideias para anúncios no YouTube Ads | Marketing/YouTube |
| 69 | Roteiro YouTube Ads | Crie um roteiro de vídeo para seu anúncio no YouTube Ads | Marketing/YouTube |
| 72 | Categorização de Produtos | Categorização de produtos fácil e simplificada. Disponível apenas para Vestuário & Acessórios | E-commerce |
| 75 | Roteiro de Lives Instagram (Bullet Points) | Converta suas ideias ou bullet points em roteiros envolventes para lives no Instagram | Marketing/Instagram |
| 76 | Roteiro Completo Lives Instagram | Crie um roteiro completo com a Tess AI para suas lives no Instagram | Marketing/Instagram |

## Uso com o script `tess_api_cli.py`

Para utilizar qualquer um destes agentes com o script `tess_api_cli.py`, use o comando:

```bash
python scripts/tess_api_cli.py executar <ID> --parametros seu_arquivo.json
```

Exemplo:
```bash
python scripts/tess_api_cli.py executar 67 --parametros exemplo_linkedin.json
```

Para verificar os parâmetros específicos necessários para cada agente:

```bash
python scripts/tess_api_cli.py info <ID>
```

## Categorias Disponíveis

Os agentes TESS podem ser agrupados nas seguintes categorias:

1. **Marketing/Google Ads**: Criação de anúncios e campanhas para Google Ads
2. **Marketing/Email**: Criação de títulos e conteúdo para e-mail marketing
3. **Marketing/SEO**: Planejamento de palavras-chave e conteúdo para SEO
4. **Marketing/Social Media**: Criação de conteúdo para redes sociais
5. **Marketing/YouTube**: Criação de roteiros e ideias para anúncios em vídeo
6. **Marketing/Instagram**: Roteiros para lives e conteúdo para Instagram
7. **E-commerce**: Ferramentas específicas para lojas online 

## Importante: Diferença entre IDs de Agentes

Existem diferenças importantes na forma como os agentes TESS são identificados, dependendo do método de acesso:

### Via script `tess_api_cli.py` (este documento)

- Usa **IDs numéricos** (45, 48, 49, etc.)
- Mostra apenas os agentes acessíveis pela chave API definida no arquivo `.env`
- Lista aproximadamente 15 agentes no total
- Alguns metadados podem estar incompletos (ex: "Nome não disponível")

### Via comando `test_api_tess` no Arcee CLI

- Usa **IDs alfanuméricos descritivos** (ex: "anuncios-de-texto-no-google-ads-para-a-marca-PefqXk")
- Acessa através do adaptador Arcee, possivelmente com permissões diferentes
- Lista mais de 600 agentes no total
- Fornece nomes mais amigáveis e descritivos

Ao desenvolver integrações, é importante considerar qual sistema de identificação está sendo utilizado e manter um mapeamento entre eles se necessário. 