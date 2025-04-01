# Como Usar o Comando `test_api_tess` na Interface Arcee CLI

Este documento explica como usar o comando `test_api_tess` para interagir com a API TESS através da interface Arcee CLI, incluindo como resolver problemas comuns.

## Contexto do Problema

O comando `test_api_tess` permite testar a API TESS para listar agentes disponíveis e executar agentes específicos. No entanto, muitos usuários encontram dificuldades ao tentar executar este comando e recebem erros como `422 Unprocessable Entity`.

## Pré-requisitos

- Arcee CLI instalado
- Configurações do ambiente com API Key TESS válida

## Solução Passo a Passo

### 1. Entendendo o Problema

O comando `test_api_tess executar` falha porque cada agente TESS requer parâmetros específicos, que não são passados automaticamente pelo comando sem personalização. A API TESS retorna um erro 422 quando os parâmetros obrigatórios estão faltando.

### 2. Investigação da API TESS

Para resolver o problema, precisamos entender quais parâmetros o agente específico requer. Isso pode ser feito consultando a API TESS diretamente:

```python
import requests
import json

api_key = "1145|VibDthGQYy5QCLk01JFp2X7QA63s2c6ZEieIf5KC8f5b099b"  # Substitua pela sua chave
agent_id = 45  # ID do agente "Anúncios de Texto no Google Ads para a Marca"

response = requests.get(
    f'https://tess.pareto.io/api/agents/{agent_id}',
    headers={'Authorization': f'Bearer {api_key}'}
)

data = response.json()
questions = data.get('questions', [])
print(json.dumps(questions, indent=2))
```

A resposta mostra os parâmetros necessários:

```json
[
  {
    "type": "text",
    "name": "nome-da-empresa",
    "description": "Nome que aparecer\u00e1 nos an\u00fancios (m\u00e1x 30 caracteres)",
    "isFieldForTraining": true,
    "required": true
  },
  {
    "type": "textarea",
    "name": "descrio",
    "description": "O que \u00e9 a empresa? Descreva brevemente.",
    "isFieldForTraining": true,
    "required": true
  },
  // ... outros parâmetros
]
```

### 3. Executando Diretamente com a API

Ao invés de usar o comando `test_api_tess`, podemos fazer uma requisição direta à API TESS com todos os parâmetros necessários:

```python
import requests
import json

api_key = "1145|VibDthGQYy5QCLk01JFp2X7QA63s2c6ZEieIf5KC8f5b099b"  # Substitua pela sua chave
agent_id = 45  # ID do agente "Anúncios de Texto no Google Ads para a Marca"

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

### 4. Problemas Comuns e Soluções

#### Erro 422 (Unprocessable Entity)

Este erro ocorre quando:

- **Parâmetros obrigatórios faltando**: Cada agente TESS tem seus próprios parâmetros obrigatórios.
- **Formato incorreto**: Alguns parâmetros como `temperature` devem ser strings, não números.
- **Valores inválidos**: Parâmetros como `language` devem ser exatamente um dos valores permitidos.

**Solução**: Consultar os detalhes do agente para ver os parâmetros necessários e seus formatos corretos.

#### Problemas Específicos do Comando `test_api_tess`

O comando `test_api_tess` do Arcee CLI não está configurado para enviar todos os parâmetros necessários para cada agente, o que causa erros 422.

**Solução**: Usar diretamente a API TESS com Python ou criar um script personalizado que adicione os parâmetros necessários.

## Exemplo de Solução no Cursor Agent

Executando uma chamada direta à API TESS para criar anúncios para "Café Aroma":

```python
import requests
import json

api_key = "1145|VibDthGQYy5QCLk01JFp2X7QA63s2c6ZEieIf5KC8f5b099b"
agent_id = 45  # Anúncios de Texto no Google Ads

payload = {
    'temperature': '0.75',
    'model': 'tess-ai-light',
    'nome-da-empresa': 'Café Aroma',
    'descrio': 'Cafeteria gourmet com café de origem única e torrefação artesanal.',
    'diferenciais': 'Café de origem única, torrefação artesanal, experiência premium para amantes de café',
    'call-to-action': 'Visite-nos hoje',
    'maxlength': 140,
    'language': 'Portuguese (Brazil)',
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

## Resultado Obtido

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

## Próximos Passos Possíveis

1. **Melhoria do comando `test_api_tess`**: Adicionar suporte para envio dinâmico de parâmetros.
2. **Integração com a interface Arcee CLI**: Implementar formulários interativos para preencher os parâmetros necessários.
3. **Script auxiliar**: Criar um script Python que facilite a execução de agentes TESS com todos os parâmetros.

## Conclusão

O comando `test_api_tess` na interface Arcee CLI tem limitações quando se trata de enviar parâmetros específicos para agentes TESS. A melhor abordagem é fazer requisições diretas à API TESS, garantindo que todos os parâmetros necessários sejam enviados no formato correto.

Este documento fornece tanto o diagnóstico do problema quanto a solução aplicada, permitindo executar com sucesso agentes TESS para criar anúncios e outros conteúdos. 