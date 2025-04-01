# Dicas Avançadas para Geração de Anúncios com a API TESS

Este guia contém dicas detalhadas para obter os melhores resultados ao gerar anúncios para Google Ads utilizando a API TESS com o script `tess_api_cli.py`.

## Escrevendo Descrições Eficazes

A qualidade das descrições fornecidas afeta diretamente a qualidade dos anúncios gerados. Recomendamos:

### Para o campo `descrio` (Descrição da empresa/produto):

- **Seja específico**: Em vez de "Cafeteria com bons cafés", use "Cafeteria gourmet especializada em grãos de origem única da América Central, com torrefação artesanal diária"
- **Inclua seu público-alvo**: "...para amantes de café exigentes" ou "...para pequenas e médias empresas que desejam aumentar sua presença online"
- **Mencione benefícios tangíveis**: "...que aumenta a produtividade em 30%" ou "...que economiza até 40% em custos operacionais"
- **Use linguagem clara e concisa**: Evite jargões técnicos a menos que seu público seja especializado
- **Inclua números quando possível**: "10 anos de experiência", "mais de 1000 clientes satisfeitos"

### Para o campo `diferenciais`:

- **Liste 3-6 diferenciais realmente únicos**: Evite afirmações genéricas como "qualidade" ou "bom atendimento"
- **Seja específico e mensurável**: "Atendimento em até 30 minutos", "Garantia de 5 anos", "Devolução em 24 horas"
- **Destaque aspectos únicos**: O que te diferencia realmente dos concorrentes?
- **Separe cada diferencial com vírgulas**: "Torrefação diária, grãos orgânicos, baristas premiados, ambiente aconchegante"

### Para o campo `call-to-action`:

- **Use verbos de ação**: "Agende", "Compre", "Visite", "Experimente", "Solicite"
- **Crie senso de urgência**: "Comece hoje", "Agende agora", "Vagas limitadas"
- **Destaque benefícios imediatos**: "Agende uma consulta gratuita", "Solicite uma demonstração sem compromisso"
- **Seja direto e claro**: O CTA deve comunicar exatamente o que você quer que o cliente faça

## Ajustando Parâmetros para Melhores Resultados

### Temperatura (`temperature`)

O parâmetro `temperature` controla a criatividade e randomização das respostas:

- **"0.0"** - Mais determinístico, respostas mais previsíveis e conservadoras
- **"0.3" a "0.5"** - Bom para anúncios mais técnicos ou formais
- **"0.7" a "0.8"** - Valor recomendado para a maioria dos anúncios, bom equilíbrio entre criatividade e relevância
- **"0.9" a "1.0"** - Mais criatividade, bom para anúncios que precisam ser muito diferentes ou chamar muita atenção

### Tamanho Máximo (`maxlength`)

- **90-140** - Ideal para anúncios de Google Ads (respeita os limites da plataforma)
- **200-300** - Se você deseja mais opções ou anúncios mais detalhados para posterior edição
- **400+** - Para obter mais contexto e explicações sobre as escolhas do modelo

### Idioma (`language`)

Use exatamente os valores suportados pela API:
- "Portuguese (Brazil)" - Não use "pt-br" ou apenas "Portuguese"
- "English (US)" - Não use "en" ou apenas "English"

## Melhores Práticas por Tipo de Negócio

Com base nos nossos testes com diferentes tipos de negócio, recomendamos:

### Cafeterias e Restaurantes

```json
{
  "descrio": "Descreva a origem dos alimentos, método de preparo, ambiente e experiência sensorial",
  "diferenciais": "Foque em ingredientes exclusivos, processos artesanais, premiações, história do local",
  "call-to-action": "Chame para uma experiência sensorial: 'Prove nosso café premiado hoje'"
}
```

### Serviços Profissionais (Agências, Consultorias)

```json
{
  "descrio": "Enfatize resultados concretos, cases de sucesso, ROI e metodologia",
  "diferenciais": "Destaque certificações, anos de experiência, garantias, metodologia proprietária, atendimento diferenciado",
  "call-to-action": "Ofereça diagnóstico ou consulta inicial gratuita: 'Agende sua análise gratuita'"
}
```

### Produtos e E-commerce

```json
{
  "descrio": "Descreva as características técnicas, materiais, processo de fabricação, benefícios práticos",
  "diferenciais": "Foque em garantia estendida, frete grátis, exclusividade, tecnologia proprietária",
  "call-to-action": "Destaque promoções por tempo limitado: 'Compre hoje com 20% de desconto'"
}
```

### Seguro e Serviços Financeiros

```json
{
  "descrio": "Ênfase em segurança, tranquilidade e suporte em momentos críticos",
  "diferenciais": "Destaque tempos de atendimento, abrangência da cobertura, facilidade de acionamento, preço competitivo",
  "call-to-action": "Ofereça cotações gratuitas: 'Solicite uma cotação personalizada grátis'"
}
```

## Exemplos de Parâmetros Otimizados

### Cafeteria Premium

```json
{
  "nome-da-empresa": "Café Aroma",
  "descrio": "Cafeteria gourmet especializada em grãos de origem única da Etiópia e Colômbia, com torrefação artesanal diária no local. Oferecemos métodos alternativos de preparo como sifão, cold brew e Aeropress, criando uma experiência completa para verdadeiros apreciadores de café.",
  "diferenciais": "Grãos torrados diariamente, métodos exclusivos de preparo, baristas campeões nacionais, ambiente aconchegante com design premiado, degustações semanais gratuitas, doces artesanais exclusivos",
  "call-to-action": "Desperte seus sentidos hoje",
  "temperature": "0.75",
  "model": "gpt-4o",
  "maxlength": 140,
  "language": "Portuguese (Brazil)"
}
```

### Consultoria de Marketing Digital

```json
{
  "nome-da-empresa": "Marketing Digital Pro",
  "descrio": "Agência especializada em marketing digital com foco em resultados mensuráveis e ROI para pequenas e médias empresas. Nossa abordagem data-driven já aumentou em média 43% o tráfego orgânico e 67% a taxa de conversão dos nossos clientes nos primeiros 3 meses.",
  "diferenciais": "Especialistas certificados pelo Google e Meta, dashboard de métricas em tempo real para o cliente, relatórios semanais transparentes, garantia de aumento de tráfego em 90 dias ou seu dinheiro de volta, metodologia exclusiva ROI-First",
  "call-to-action": "Transforme visitantes em clientes agora",
  "temperature": "0.8",
  "model": "gpt-4o",
  "maxlength": 140,
  "language": "Portuguese (Brazil)"
}
```

## Resolução de Problemas Comuns

### Anúncios Muito Genéricos

Se os anúncios gerados parecem muito genéricos:

- Adicione mais detalhes específicos na descrição
- Aumente o valor de `temperature` para 0.8-0.9
- Forneça diferenciais mais concretos e únicos
- Teste diferentes modelos de linguagem (GPT-4o vs Claude 3.5 Sonnet)

### Anúncios Não Capturam o Tom da Marca

Se os anúncios não refletem adequadamente o tom da sua marca:

- Adicione informações sobre o tom desejado na descrição (ex: "Nossa marca tem um tom descontraído e jovem")
- Inclua exemplos de comunicação no campo de diferenciais
- Ajuste `temperature` para 0.7-0.8 para mais criatividade

### Anúncios Longos Demais

Para garantir que os anúncios respeiem os limites do Google Ads:

- Confirme que `maxlength` está configurado para 140 ou menos
- Seja mais conciso na sua descrição e diferenciais
- Use o parâmetro `model` "gpt-4o" que tende a respeitar melhor os limites

## Conclusão

A geração de anúncios eficazes com a API TESS depende principalmente da qualidade dos inputs fornecidos. Ao seguir estas dicas, você maximizará a qualidade dos anúncios gerados e economizará tempo no processo criativo. 

## Apêndice: Sistemas de Identificação dos Agentes TESS

Ao trabalhar com a API TESS, é importante estar ciente de que existem dois sistemas diferentes de identificação para os agentes, dependendo do método de acesso:

### 1. Via Script `tess_api_cli.py` (API Direta)

Quando você acessa diretamente a API TESS usando o script `tess_api_cli.py` ou chamadas diretas à API:

```bash
python scripts/tess_api_cli.py listar
```

Os agentes são identificados por:
- IDs numéricos simples (45, 48, 49, etc.)
- Lista limitada (aproximadamente 15 agentes)
- Exemplo: `ID: 45 - Anúncios Google Ads`

### 2. Via Comando `test_api_tess` (Arcee CLI)

Quando você acessa a API TESS através do comando `test_api_tess` no terminal interativo do Arcee:

```bash
arcee chat
> test_api_tess listar
```

Os agentes são identificados por:
- IDs alfanuméricos descritivos (ex: "anuncios-de-texto-no-google-ads-para-a-marca-PefqXk")
- Lista extensa (mais de 600 agentes)
- Exemplo: `ID: anuncios-de-texto-no-google-ads-para-a-marca-PefqXk - Anúncios de texto Google Ads`

### Mapeamento entre Sistemas

Para facilitar o uso, aqui está um mapeamento parcial entre os dois sistemas para os agentes mais utilizados:

| ID Numérico (API Direta) | ID Descritivo (Arcee CLI) | Descrição |
|--------------------------|----------------------------|-----------|
| 45 | anuncios-de-texto-no-google-ads-para-a-marca-PefqXk | Anúncios para campanhas da marca no Google Ads |
| 48 | anuncios-de-texto-no-google-ads-para-produtos-ou-servicos-mF37hV | Anúncios para produtos/serviços no Google Ads |
| 49 | anuncios-para-performance-max-no-google-ads-7F3shK | Anúncios para Performance Max no Google Ads |
| 67 | transformar-texto-em-post-para-linkedin-mF37hV | Posts para LinkedIn |

### Considerações para Integração

Se você estiver desenvolvendo scripts ou integrações que alternam entre os dois métodos de acesso:

1. Mantenha um mapeamento entre os dois sistemas de IDs
2. Documente claramente qual sistema está sendo usado em cada parte do código
3. Considere padronizar em um único método de acesso se possível
4. Teste a disponibilidade de agentes em ambos os sistemas antes de depender de um ID específico 