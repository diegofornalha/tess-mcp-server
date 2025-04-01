# Scripts Utilitários para TESS e MCP

Este diretório contém scripts utilitários para interação com o TESS, MCP e outros serviços relacionados.

## TESS API CLI (`tess_api_cli.py`)

Uma ferramenta de linha de comando para interagir diretamente com a API TESS, facilitando a listagem, consulta e execução de agentes TESS.

### Recursos

- Listar todos os agentes TESS disponíveis
- Consultar informações detalhadas sobre um agente específico
- Listar modelos disponíveis com recomendações
- Executar agentes TESS com parâmetros personalizados
- Suporte para Claude 3.7 Sonnet com Extended Thinking
- Suporte a diferentes formatos de saída (texto, JSON, formatado)
- Carregar parâmetros de arquivos JSON
- Tratamento de erros específicos da API TESS

### Pré-requisitos

- Python 3.6+
- Bibliotecas: requests, dotenv
- API Key TESS válida

### Instalação

Não é necessário instalar. Certifique-se apenas de que o script tenha permissão de execução:

```bash
chmod +x tess_api_cli.py
```

### Uso

#### Listar agentes disponíveis:

```bash
./tess_api_cli.py listar
```

#### Obter informações detalhadas sobre um agente específico:

```bash
./tess_api_cli.py info 45  # onde 45 é o ID do agente
```

#### Listar modelos disponíveis:

```bash
./tess_api_cli.py modelos
```

#### Executar um agente com parâmetros em linha de comando:

```bash
./tess_api_cli.py executar 45 \
  --nome-da-empresa "Café Aroma" \
  --descrio "Cafeteria gourmet com café de origem única" \
  --diferenciais "Café de origem única, torrefação artesanal" \
  --call-to-action "Visite-nos hoje" \
  --temperature "0.75" \
  --language "Portuguese (Brazil)" \
  --maxlength 140
```

#### Executar um agente com Claude 3.7 Sonnet e Extended Thinking:

```bash
./tess_api_cli.py executar 45 \
  --nome-da-empresa "Café Aroma" \
  --descrio "Cafeteria gourmet com café de origem única" \
  --diferenciais "Café de origem única, torrefação artesanal" \
  --call-to-action "Visite-nos hoje" \
  --model "claude-3-7-sonnet@20250219" \
  --extended_thinking True
```

#### Executar um agente com parâmetros de um arquivo JSON:

```bash
./tess_api_cli.py executar 45 --parametros exemplo_anuncios_cafe.json
```

#### Escolher o formato de saída:

```bash
./tess_api_cli.py executar 45 --parametros exemplo_anuncios_cafe.json --formato-saida json
```

### Exemplo de arquivo de parâmetros (JSON)

Veja o exemplo em `exemplo_anuncios_cafe.json`:

```json
{
  "nome-da-empresa": "Café Aroma",
  "descrio": "Cafeteria gourmet com café de origem única e torrefação artesanal.",
  "diferenciais": "Café de origem única, torrefação artesanal, experiência premium para amantes de café",
  "call-to-action": "Visite-nos hoje",
  "temperature": "0.75",
  "model": "gpt-4o",
  "maxlength": 140,
  "language": "Portuguese (Brazil)"
}
```

Outro exemplo disponível é `exemplo_anuncios_mkt.json`, para agência de marketing digital:

```json
{
  "nome-da-empresa": "Marketing Digital Pro",
  "descrio": "Agência especializada em marketing digital com foco em resultados e ROI. Oferecemos serviços completos de SEO, redes sociais, Google Ads e marketing de conteúdo para pequenas e médias empresas que querem aumentar sua presença online e gerar mais leads qualificados.",
  "diferenciais": "Estratégias personalizadas, métricas em tempo real, especialistas certificados em Google Ads e Meta, metodologia comprovada, atendimento personalizado, relatórios transparentes mensais, retorno sobre investimento garantido",
  "call-to-action": "Agende uma consulta gratuita",
  "temperature": "0.75",
  "model": "gpt-4o",
  "maxlength": 140,
  "language": "Portuguese (Brazil)"
}
```

E para corretora de seguros, veja o exemplo em `exemplo_anuncios_seguros.json`:

```json
{
  "nome-da-empresa": "Seguros Confiança",
  "descrio": "Corretora de seguros especializada em planos personalizados para vida, auto, residencial e empresarial. Oferecemos as melhores coberturas do mercado com preços competitivos e atendimento 24/7.",
  "diferenciais": "Atendimento 24/7, sinistro resolvido em até 48h, planos personalizados, melhor preço garantido, especialistas em cada modalidade de seguro, assistência completa",
  "call-to-action": "Solicite uma cotação grátis",
  "temperature": "0.75",
  "model": "gpt-4o",
  "maxlength": 140,
  "language": "Portuguese (Brazil)"
}
```

### Modelos recomendados

Os seguintes modelos são recomendados para uso com a API TESS:

1. **GPT-4o** (`gpt-4o`): Modelo padrão recomendado, com excelente performance para geração de texto e processamento de contexto. Versão avançada do GPT-4 com recursos multimodais.

2. **Claude 3.5 Sonnet** (`claude-3-5-sonnet-20240620`): Bom balanceamento entre velocidade e qualidade. Recomendado para tarefas que exigem raciocínio mais complexo.

3. **GPT-4o mini** (`gpt-4o-mini`): Versão mais rápida e econômica do GPT-4o, ideal para tarefas que não exigem máxima qualidade.

> **Nota:** O modelo Claude 3.7 Sonnet com Extended Thinking não está disponível diretamente na API TESS. O script foi configurado para usar GPT-4o como modelo padrão, que oferece ótima qualidade e compatibilidade com a API.

### Extended Thinking

O recurso **Extended Thinking** está disponível para o modelo Claude 3.7 Sonnet e permite um raciocínio mais detalhado, passo a passo, em problemas complexos. Este modo faz com que o modelo:

- Divida problemas complexos em etapas menores
- Raciocine de forma mais aprofundada, considerando múltiplas alternativas
- Forneça explicações mais detalhadas para suas decisões
- Avalie criticamente seu próprio raciocínio

Para habilitar este recurso, use o parâmetro `extended_thinking`:

```bash
./tess_api_cli.py executar 45 --model "claude-3-7-sonnet@20250219" --extended_thinking True
```

### Vantagens sobre o comando `test_api_tess`

O `tess_api_cli.py` oferece várias vantagens em relação ao comando `test_api_tess`:

1. **Parâmetros completos**: Envia automaticamente todos os parâmetros necessários para cada agente
2. **Validação simples**: Exibe mensagens de erro mais descritivas
3. **Formatos de saída**: Suporta diferentes formatos de saída, incluindo JSON e formatado
4. **Flexibilidade**: Aceita parâmetros tanto de linha de comando quanto de arquivo JSON
5. **Documentação completa**: Exibe informações detalhadas sobre cada agente e seus parâmetros
6. **Suporte a modelos avançados**: Configurado para usar o GPT-4o por padrão, garantindo melhor compatibilidade

## Outros Scripts

- `setup_arcee_cli.sh`: Script para instalação do Arcee CLI
- `start_streamlit.sh`: Inicia a aplicação Streamlit
- `iniciar_tess_mcp_dev.sh`: Inicia o ambiente de desenvolvimento TESS MCP
- `iniciar_tess_mcp_prod.sh`: Inicia o ambiente de produção TESS MCP
- `find_tools_usage.py`: Utilitário para localizar uso de ferramentas
- `migrate_tools.py`: Script para migração de ferramentas

## Dicas Práticas para o uso do `tess_api_cli.py`

Baseado em nossa experiência com o uso intensivo da ferramenta, compartilhamos algumas dicas práticas:

### Otimizando os Resultados

1. **Consulte o agente antes de executar**: Use `./tess_api_cli.py info <id>` para ver exatamente quais parâmetros o agente espera antes de tentar executá-lo.

2. **Verifique os modelos disponíveis**: Use `./tess_api_cli.py modelos` para listar os modelos disponíveis e evitar erros 422 relacionados a modelos inválidos.

3. **Formate corretamente os valores**: Alguns parâmetros como `temperature` precisam ser enviados como string (ex: "0.75") e não como números.

4. **Preferência por arquivos JSON**: Para execuções frequentes ou parâmetros complexos, prefira usar arquivos JSON em vez de parâmetros na linha de comando.

### Solução de Problemas Comuns

1. **Erro 422 (Unprocessable Entity)**:
   - Verifique se todos os parâmetros obrigatórios estão presentes
   - Confirme se está usando um modelo válido (use `modelos` para listar)
   - Verifique o formato dos parâmetros (especialmente `temperature` como string)

2. **Erro com modelo Claude 3.7 Sonnet**:
   - Atualmente, o Claude 3.7 Sonnet com Extended Thinking não está disponível na API TESS
   - Use GPT-4o como alternativa recomendada

3. **Respostas incompletas ou incorretas**:
   - Tente aumentar o valor de `maxlength` para obter respostas mais completas
   - Ajuste o valor de `temperature` para equilibrar criatividade vs. precisão
   - Forneça descrições mais detalhadas nos parâmetros de entrada

### Comparação entre Arquivos de Exemplo

Após testar com diferentes tipos de negócio, observamos que:

| Exemplo | Detalhamento | Especificidade | Qualidade dos Anúncios |
|---------|--------------|----------------|------------------------|
| Café Aroma | Alto | Muito específico | Excelente |
| Marketing Digital | Alto | Específico para serviços | Muito boa |
| Seguros | Médio | Abrange múltiplos produtos | Boa, mas mais genérica |

Quanto mais detalhada e específica a descrição do negócio e seus diferenciais, melhores são os resultados obtidos. 

Para dicas mais detalhadas sobre como criar parâmetros eficazes para diferentes tipos de negócio, consulte o arquivo [usando_api_tess_dicas.md](usando_api_tess_dicas.md) com exemplos e práticas recomendadas.

## Scripts de utilitário

Este diretório contém scripts úteis para desenvolvimento e manutenção.

### update_npm.sh

Script para atualizar facilmente o pacote no npm.

**Descrição**: Automatiza o processo de atualização da versão, empacotamento e publicação do pacote `@diegofornalha/crew-ai-tess-pareto` no registro npm.

**Uso**:
```bash
./scripts/update_npm.sh
```

**Funcionalidades**:
- Verifica se você está logado no npm
- Permite escolher entre atualização de versão patch, minor, major, ou especificar uma versão
- Detecta e oferece remover dependências cíclicas
- Executa testes antes da publicação (opcional)
- Permite visualizar o conteúdo do pacote antes de publicar
- Solicita confirmação antes de publicar no npm

**Exemplo de fluxo**:
1. Execute o script: `./scripts/update_npm.sh`
2. Escolha o tipo de atualização de versão
3. Confirme a remoção de dependências cíclicas, se detectadas
4. Escolha se deseja executar testes
5. Decida se quer verificar o conteúdo do pacote
6. Confirme a publicação no npm

**Requisitos**:
- Node.js e npm instalados
- Autenticação ativa no npm
- Projeto configurado corretamente com package.json válido 