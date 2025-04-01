# Guia de Integração com a API TESS

Este documento explica como executar agentes TESS diretamente através da API, usando Python ou outras linguagens de programação.

## Introdução

A API TESS permite acessar agentes especializados para várias tarefas, como criação de anúncios, posts para redes sociais, e-mails, entre outros. Este guia demonstra como fazer requisições diretas para a API, sem depender de ferramentas intermediárias.

## Pré-requisitos

- API Key TESS válida
- Python com a biblioteca `requests` instalada
- Conhecimento básico sobre requisições HTTP

## Passo a Passo para Execução de Agentes TESS

### 1. Listar Agentes Disponíveis

Primeiro, é importante verificar quais agentes estão disponíveis na sua conta:

```python
import requests
import json

api_key = "SUA_API_KEY_TESS"  # Substitua pela sua chave

response = requests.get(
    'https://tess.pareto.io/api/agents',
    headers={'Authorization': f'Bearer {api_key}'}
)

print(f"Status: {response.status_code}")
print(response.text[:500])  # Exibir os primeiros 500 caracteres
```

### 2. Consultar Detalhes do Agente

Antes de executar um agente, é importante verificar quais parâmetros ele espera receber:

```python
import requests
import json

api_key = "SUA_API_KEY_TESS"  # Substitua pela sua chave
agent_id = 45  # ID do agente que você deseja consultar

response = requests.get(
    f'https://tess.pareto.io/api/agents/{agent_id}',
    headers={'Authorization': f'Bearer {api_key}'}
)

# Extrair os parâmetros necessários
data = response.json()
questions = data.get('questions', [])
print(json.dumps(questions, indent=2))
```

Este passo é essencial, pois cada agente TESS pode exigir parâmetros diferentes e específicos.

### 3. Executar um Agente

Depois de entender quais parâmetros são necessários, você pode executar o agente:

```python
import requests
import json

api_key = "SUA_API_KEY_TESS"  # Substitua pela sua chave
agent_id = 45  # ID do agente "Anúncios de Texto no Google Ads para a Marca"

# Parâmetros específicos para este agente
payload = {
    'temperature': '0.75',  # Deve ser string e um dos valores permitidos
    'model': 'tess-ai-light',
    'nome-da-empresa': 'Café Aroma',
    'descrio': 'Cafeteria gourmet com café de origem única e torrefação artesanal.',
    'diferenciais': 'Café de origem única, torrefação artesanal, experiência premium para amantes de café',
    'call-to-action': 'Visite-nos hoje',
    'maxlength': 140,
    'language': 'Portuguese (Brazil)',  # Deve ser um dos valores exatos permitidos
    'waitExecution': True
}

response = requests.post(
    f'https://tess.pareto.io/api/agents/{agent_id}/execute',
    headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    },
    json=payload
)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    output = result.get('responses', [])[0].get('output', '')
    print("\n===== RESULTADO =====\n")
    print(output)
else:
    print("Erro:")
    print(response.text)
```

## Tratamento de Erros Comuns

### Erro 422 (Unprocessable Entity)

Este erro geralmente ocorre quando:

1. **Parâmetros obrigatórios faltando**: Cada agente TESS exige parâmetros específicos.
2. **Formato de parâmetro incorreto**: Alguns parâmetros como `temperature` devem ser strings, não números.
3. **Valores inválidos**: Alguns parâmetros como `language` devem ser exatamente um dos valores permitidos.

Exemplo de erro e solução:

```
{"message":"The nome-da-empresa field is required. (and 6 more errors)","errors":{"nome-da-empresa":["The nome-da-empresa field is required."]}}
```

**Solução**: Adicionar todos os campos obrigatórios ao payload.

### Erro 401 (Unauthorized)

Ocorre quando a API key está inválida ou expirada.

**Solução**: Verificar se a API key está correta e se ainda é válida.

## Exemplo Completo com Agente de Anúncios do Google Ads

Aqui está um exemplo completo que gera anúncios para uma cafeteria:

```python
import requests
import json

# Configurações
api_key = "1145|VibDthGQYy5QCLk01JFp2X7QA63s2c6ZEieIf5KC8f5b099b"  # Substitua pela sua chave
agent_id = 45  # ID do agente "Anúncios de Texto no Google Ads para a Marca"

# Parâmetros do agente
payload = {
    'temperature': '0.75',  # Nota: deve ser string
    'model': 'tess-ai-light',
    'nome-da-empresa': 'Café Aroma',
    'descrio': 'Cafeteria gourmet com café de origem única e torrefação artesanal.',
    'diferenciais': 'Café de origem única, torrefação artesanal, experiência premium para amantes de café',
    'call-to-action': 'Visite-nos hoje',
    'maxlength': 140,
    'language': 'Portuguese (Brazil)',  # Deve ser exatamente um dos valores permitidos
    'waitExecution': True
}

# Fazer a requisição
response = requests.post(
    f'https://tess.pareto.io/api/agents/{agent_id}/execute',
    headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    },
    json=payload
)

print(f"Status: {response.status_code}")

# Processamento do resultado
if response.status_code == 200:
    result = response.json()
    output = result.get('responses', [])[0].get('output', '')
    print("\n===== ANÚNCIOS GERADOS PARA CAFÉ AROMA =====\n")
    print(output)
else:
    print("Erro:")
    print(response.text)
```

## Resultado Esperado

O exemplo acima deve gerar uma saída semelhante a:

```
===== ANÚNCIOS GERADOS PARA CAFÉ AROMA =====

### Opções de Título:

**A) Com nome da marca:**
1. Café Aroma: Sabor Único
2. Café Aroma - Torrefação Artesanal
3. Experimente o Café Aroma
4. Café Aroma: Para Amantes de Café

**B) Com diferenciais e benefícios:**
5. Café de Origem Única
6. Torrefação Artesanal Premium
7. Experiência de Café Exclusiva
8. Sabor Inigualável do Café

**C) Com call-to-action:**
9. Descubra o Melhor Café
10. Peça Seu Café Agora
11. Saboreie um Café Premium
12. Compre Seu Café Hoje

### Opções de Descrição:
1. Descubra o sabor único do Café Aroma. Café de origem única e torrefação artesanal. Peça já.
2. Experimente a experiência premium do Café Aroma. Torrefação artesanal para amantes de café.
3. Café Aroma oferece o melhor em café com torrefação artesanal. Adquira o seu agora mesmo.
4. Aprecie um café de origem única com Café Aroma. Sabor e qualidade que você vai adorar.
```

## Considerações Importantes

1. **Parâmetros específicos**: Cada agente TESS exige parâmetros diferentes. Sempre consulte os detalhes do agente antes.
2. **Valores permitidos**: Alguns parâmetros têm listas restritas de valores permitidos.
3. **Tipos de dados**: Preste atenção ao tipo de dado esperado em cada campo.
4. **Limitações de uso**: A API TESS tem limites de uso baseados na sua assinatura.

## Recursos Adicionais

- [Documentação Oficial da API TESS](https://docs.tess.pareto.io/api/introduction)
- [Endpoint de Execução de Agentes](https://docs.tess.pareto.io/api/endpoints/agents/execute)
- [Endpoint Compatível com OpenAI](https://docs.tess.pareto.io/api/endpoints/agents/execute_openai_compatible)

Esperamos que este guia ajude na integração com a API TESS para suas necessidades de geração de conteúdo! 