# Guia de Integração com a API TESS

Este guia fornece instruções detalhadas para integração com a API TESS para geração de conteúdo, especialmente para criação de anúncios para Google Ads.

## Pré-requisitos

- Chave de API TESS válida
- Python 3.6 ou superior
- Bibliotecas Python: requests, dotenv (para carregar variáveis de ambiente)

## Configuração Inicial

1. Configure sua chave de API TESS como variável de ambiente:

```bash
export TESS_API_KEY="sua_chave_api_tess"
```

Ou adicione-a ao arquivo `.env`:

```
TESS_API_KEY=sua_chave_api_tess
```

2. Use o script `tess_api_cli.py` fornecido na pasta `/scripts` para facilitar a interação com a API.

## Listando Agentes Disponíveis

Para listar todos os agentes disponíveis na API TESS:

```bash
python scripts/tess_api_cli.py listar
```

## Consultando Detalhes de um Agente

Para obter detalhes sobre um agente específico, incluindo parâmetros necessários:

```bash
python scripts/tess_api_cli.py info 45  # onde 45 é o ID do agente para anúncios Google Ads
```

## Modelos LLM Disponíveis

Para verificar os modelos de linguagem disponíveis:

```bash
python scripts/tess_api_cli.py modelos
```

### Modelos Recomendados

- **GPT-4o** (`gpt-4o`): Modelo recomendado para geração de anúncios, com melhor compatibilidade
- **Claude 3.5 Sonnet** (`claude-3-5-sonnet-20240620`): Alternativa com bom balanceamento entre qualidade e velocidade
- **GPT-4o mini** (`gpt-4o-mini`): Opção mais rápida, ideal para testes

> **Importante**: O modelo Claude 3.7 Sonnet com Extended Thinking não está disponível diretamente na API TESS.

## Parâmetros para Geração de Anúncios (Agente ID 45)

O agente com ID 45 é especializado na criação de anúncios para Google Ads e requer os seguintes parâmetros:

| Parâmetro | Descrição | Tipo | Obrigatório |
|-----------|-----------|------|-------------|
| nome-da-empresa | Nome da empresa ou marca | string | Sim |
| descrio | Descrição do produto/serviço | string | Sim |
| diferenciais | Diferenciais competitivos | string | Sim |
| call-to-action | CTA para os anúncios | string | Sim |
| temperature | Criatividade (0-1) | string | Sim |
| model | Modelo de linguagem | string | Sim |
| maxlength | Tamanho máximo (caracteres) | integer | Sim |
| language | Idioma dos anúncios | string | Sim |

## Geração de Anúncios com Linha de Comando

```bash
python scripts/tess_api_cli.py executar 45 \
  --nome-da-empresa "Marketing Digital Pro" \
  --descrio "Agência especializada em marketing digital com foco em resultados e ROI." \
  --diferenciais "Estratégias personalizadas, métricas em tempo real, especialistas certificados" \
  --call-to-action "Agende uma consulta gratuita" \
  --model "gpt-4o" \
  --temperature "0.75" \
  --maxlength 140 \
  --language "Portuguese (Brazil)"
```

## Geração de Anúncios com Arquivo JSON

1. Crie um arquivo JSON com os parâmetros (exemplo: `anuncios_mkt.json`):

```json
{
  "nome-da-empresa": "Marketing Digital Pro",
  "descrio": "Agência especializada em marketing digital com foco em resultados e ROI. Oferecemos serviços completos de SEO, redes sociais, Google Ads e marketing de conteúdo para pequenas e médias empresas.",
  "diferenciais": "Estratégias personalizadas, métricas em tempo real, especialistas certificados, metodologia comprovada",
  "call-to-action": "Agende uma consulta gratuita",
  "temperature": "0.75",
  "model": "gpt-4o",
  "maxlength": 140,
  "language": "Portuguese (Brazil)"
}
```

2. Execute o comando com o arquivo de parâmetros:

```bash
python scripts/tess_api_cli.py executar 45 --parametros anuncios_mkt.json
```

## Tratamento de Erros Comuns

### Erro 422 (Unprocessable Entity)

Este erro ocorre quando:
- Parâmetros obrigatórios estão faltando
- O valor de `model` não é válido
- O formato de um parâmetro está incorreto

Solução: Verifique se todos os parâmetros obrigatórios estão presentes e no formato correto. Use `info` para consultar os parâmetros e `modelos` para ver os modelos disponíveis.

```bash
python scripts/tess_api_cli.py info 45  # Verifica parâmetros necessários
python scripts/tess_api_cli.py modelos   # Verifica modelos disponíveis
```

### Erro 401 (Unauthorized)

Este erro ocorre quando a chave de API é inválida ou expirou.

Solução: Verifique sua chave de API e atualize-a se necessário.

## Formatos de Saída

O script `tess_api_cli.py` suporta diferentes formatos de saída:

```bash
# Saída formatada (padrão)
python scripts/tess_api_cli.py executar 45 --parametros anuncios_mkt.json --formato-saida formatado

# Saída em JSON
python scripts/tess_api_cli.py executar 45 --parametros anuncios_mkt.json --formato-saida json

# Saída em texto puro
python scripts/tess_api_cli.py executar 45 --parametros anuncios_mkt.json --formato-saida texto
```

## Exemplo de Resposta (Anúncios Gerados)

A execução bem-sucedida retornará títulos e descrições para anúncios do Google Ads:

```
=== ANÚNCIOS GERADOS ===

=== TÍTULOS ===
Grupo A – Com nome da marca:
1. Marketing Digital Pro
2. Pro Digital: Resultados Reais
3. Mídia Paga com a Pro
4. Anúncios com a Pro

Grupo B – Com diferenciais e benefícios:
5. Estratégia Personalizada
6. Relatórios Transparentes
7. ROI Garantido Toda Semana
8. Métricas em Tempo Real

Grupo C – Com call-to-action:
9. Invista no Digital Já
10. Aumente Seu Retorno Hoje
11. Comece a Vender Online
12. Gere Leads com Tráfego Pago

=== DESCRIÇÕES ===
1. Comece com a Marketing Digital Pro e tenha retorno garantido no seu investimento!
2. Invista com a Marketing Digital Pro e receba relatórios mensais claros e precisos.
3. Alcance mais com a Marketing Digital Pro: estratégia certa, retorno real.
4. Resultados reais com especialistas Google e Meta da Marketing Digital Pro.
5. Marketing Digital Pro: personalize, acompanhe e venda mais com tráfego pago.
6. Gere vendas com a Marketing Digital Pro. Atendimento e estratégia sob medida!
7. Métricas em tempo real com a Marketing Digital Pro. Saiba o que funciona!
8. Mais performance com a Marketing Digital Pro: sua verba bem investida.
9. Aumente conversões com a Marketing Digital Pro. Relatórios e ROI garantido.
10. Anuncie com quem entende: Marketing Digital Pro. Resultados com transparência.
```

## Recursos Adicionais

- [Documentação Oficial da API TESS](https://tess.pareto.io/docs)
- [Exemplos de Uso em Diferentes Linguagens](https://tess.pareto.io/examples)
- [Página de Status da API TESS](https://status.tess.pareto.io) 

## Lições Aprendidas

Durante a implementação e testes da integração com a API TESS, descobrimos vários pontos importantes que podem ajudar outros desenvolvedores:

### Compatibilidade de Modelos

- **GPT-4o vs Claude 3.7**: Embora o Claude 3.7 Sonnet com Extended Thinking seja um modelo avançado, descobrimos que não está disponível diretamente na API TESS. O GPT-4o mostrou ótima compatibilidade e resultados consistentes em nossos testes.

- **Formato dos nomes de modelos**: É importante usar exatamente o formato de nome de modelo listado pela API. Por exemplo, `claude-3-5-sonnet-20240620` em vez de `claude-3-5-sonnet@20240620`. Verificar com o comando `modelos` evita este tipo de erro.

- **Lista de modelos recomendados**:
  1. `gpt-4o`: Melhor equilíbrio entre qualidade e compatibilidade
  2. `claude-3-5-sonnet-20240620`: Boa alternativa com resultados de qualidade
  3. `gpt-4o-mini`: Versão mais rápida e econômica para testes

### Tratamento de Erros Específicos

- **Erro 422 com modelos**: Se receber erro 422 mencionando "The selected model is invalid", isso indica que o nome do modelo não está no formato esperado pela API ou não está disponível. Use o comando `modelos` para listar os modelos válidos.

- **Erro 422 com parâmetros**: Certifique-se de que todos os parâmetros estão no formato correto. Parâmetros como `temperature` podem exigir valores específicos (como strings) mesmo quando representam números.

### Considerações sobre Parâmetros

- **Formatação de temperatura**: O parâmetro `temperature` deve ser enviado como string, não como número, e aceita valores como "0", "0.75", "1".

- **Idiomas suportados**: O parâmetro `language` deve usar os valores exatos suportados, como "Portuguese (Brazil)" em vez de "pt-br" ou apenas "Portuguese".

### Otimização de Resultados

Nossos testes com diferentes tipos de negócios (cafeteria, marketing digital, seguros) revelaram algumas práticas para obter melhores resultados:

1. **Descrições detalhadas**: Fornecer descrições mais detalhadas e específicas resulta em anúncios de melhor qualidade.

2. **Diferenciais claros**: Listar 3-6 diferenciais específicos e mensuráveis melhora significativamente a qualidade dos anúncios.

3. **Call-to-action direto**: Instruções de ação claras como "Agende uma consulta gratuita" ou "Solicite uma cotação grátis" geram melhores resultados do que CTAs vagos.

4. **Ajuste de temperatura**: Para anúncios mais criativos, valores de temperatura entre 0.7 e 0.8 parecem fornecer um bom equilíbrio entre criatividade e relevância.

### Comparação de Desempenho entre Modelos

Em nossos testes com a geração de anúncios para Google Ads:

| Modelo | Qualidade | Velocidade | Compatibilidade | Observações |
|--------|-----------|------------|-----------------|-------------|
| GPT-4o | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Melhor equilíbrio geral e compatibilidade |
| Claude 3.5 Sonnet | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Bons resultados, mas ocasionalmente com falhas de compatibilidade |
| GPT-4o mini | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Mais rápido, mas com qualidade ligeiramente inferior |

### Diferenças entre Acessos à API TESS

Durante nossos testes, descobrimos diferenças importantes na forma como os agentes TESS são listados e acessados dependendo do método utilizado:

#### 1. Acesso Direto via API (tess_api_cli.py)

Quando acessamos diretamente a API TESS usando o script `tess_api_cli.py`:

- Os agentes são identificados por **IDs numéricos simples** (45, 48, 49...)
- Apenas um subconjunto limitado de agentes é visível (cerca de 15)
- As descrições são mostradas, mas os nomes podem aparecer como "Nome não disponível"
- O acesso é determinado pela chave API definida no arquivo `.env`

```bash
python scripts/tess_api_cli.py listar
```

Exemplo de resultado:
```
ID: 45 - Nome não disponível
  Descrição: Use a Tess AI para criar anúncios incríveis para suas campanhas da marca no Google
```

#### 2. Acesso via Arcee CLI (test_api_tess)

Quando acessamos a API TESS através do comando `test_api_tess` no Arcee CLI:

- Os agentes são identificados por **IDs alfanuméricos descritivos** (ex: "anuncios-de-texto-no-google-ads-para-a-marca-PefqXk")
- Um conjunto muito maior de agentes é visível (mais de 600)
- Nomes mais amigáveis e descritivos são fornecidos
- O acesso ocorre através do middleware/adaptador Arcee

```bash
arcee chat
> test_api_tess listar
```

Exemplo de resultado:
```
ID: anuncios-de-texto-no-google-ads-para-a-marca-PefqXk - Anúncios de texto Google Ads
```

#### Implicações Práticas

Esta diferença tem implicações importantes para a integração:

1. **Mapeamento de IDs**: Para sistemas que precisam integrar com ambos os métodos, é necessário manter um mapeamento entre IDs numéricos e alfanuméricos
2. **Escopo de acesso**: O acesso direto via API pode ter escopo reduzido dependendo das permissões da chave API utilizada
3. **Consistência de dados**: Os metadados (nomes, descrições) podem variar entre os métodos de acesso
4. **Automação**: Scripts que alternam entre os métodos precisam considerar essas diferenças

Recomendamos documentar e padronizar qual método de acesso será utilizado em cada parte do sistema para evitar inconsistências.

A integração com a API TESS é um processo em constante evolução, e estas dicas representam nosso conhecimento atual. Recomendamos verificar regularmente a documentação oficial e os modelos disponíveis para obter os melhores resultados. 