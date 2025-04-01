#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TESS API CLI - Ferramenta para interação direta com a API TESS
Autor: Claude
Versão: 1.0.0
Data: 2023-10-17
"""

import argparse
import json
import os
import sys
import requests
from dotenv import load_dotenv
from pprint import pprint
from typing import Dict, Any, List, Optional, Union

# Carregar variáveis de ambiente do arquivo .env se existir
load_dotenv()

# Constantes
TESS_API_URL = "https://tess.pareto.io/api"
TESS_API_KEY = os.getenv("TESS_PROXY_API_KEY") or os.getenv("TESS_API_KEY")

# Configurações
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

def setup_argparse():
    """Configura e retorna o parser de argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="CLI para interagir com a API TESS de forma eficiente",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  ./tess_api_cli.py listar
  ./tess_api_cli.py info 45
  ./tess_api_cli.py modelos
  ./tess_api_cli.py executar 45 --parametros arquivo_parametros.json
  ./tess_api_cli.py executar 45 --nome-da-empresa "Café Aroma" --descrio "Cafeteria gourmet" --diferenciais "Café de origem única" --call-to-action "Visite-nos hoje" --temperature 0.75 --language "Portuguese (Brazil)" --maxlength 140
        """
    )
    
    subparsers = parser.add_subparsers(dest="comando", help="Comando a executar")
    
    # Comando: listar
    listar_parser = subparsers.add_parser("listar", help="Listar todos os agentes disponíveis")
    
    # Comando: info
    info_parser = subparsers.add_parser("info", help="Obter informações detalhadas de um agente")
    info_parser.add_argument("id", type=int, help="ID do agente")
    
    # Comando: modelos
    modelos_parser = subparsers.add_parser("modelos", help="Listar todos os modelos disponíveis")
    modelos_parser.add_argument("--agent_id", type=int, default=45, help="ID do agente para consultar (padrão: 45)")
    
    # Comando: executar
    executar_parser = subparsers.add_parser("executar", help="Executar um agente específico")
    executar_parser.add_argument("id", type=int, help="ID do agente")
    executar_parser.add_argument("--parametros", type=str, help="Arquivo JSON com os parâmetros")
    executar_parser.add_argument("--model", type=str, default="gpt-4o", 
                               help="Modelo a ser usado (padrão: gpt-4o)")
    executar_parser.add_argument("--temperature", type=str, default="0.75", help="Temperatura (0-1)")
    executar_parser.add_argument("--maxlength", type=int, default=140, help="Tamanho máximo da saída")
    executar_parser.add_argument("--language", type=str, default="Portuguese (Brazil)", help="Idioma da saída")
    executar_parser.add_argument("--extended_thinking", type=bool, default=False, 
                               help="Usar 'Extended Thinking' para raciocínio avançado (apenas para modelos Claude 3.7)")
    
    # Permitir parâmetros dinâmicos para executar
    executar_parser.add_argument("--formato-saida", type=str, choices=["texto", "json", "formatado"], 
                                default="formatado", help="Formato da saída")
    
    # Adiciona todos os parâmetros possíveis como opcionais para facilitar
    # Parâmetros conhecidos de alguns agentes TESS
    for param in [
        "nome-da-empresa", "descrio", "diferenciais", "call-to-action", 
        "prompt", "texto", "tema", "titulo", "assunto", "context", "query",
        "audience", "tone", "cta", "brand", "product"
    ]:
        executar_parser.add_argument(f"--{param}", type=str, help=f"Parâmetro '{param}' para o agente")
    
    return parser

def check_api_key() -> bool:
    """Verifica se a chave da API TESS está disponível."""
    if not TESS_API_KEY:
        print("Erro: Chave da API TESS não encontrada!")
        print("Por favor, defina a variável de ambiente TESS_API_KEY ou TESS_PROXY_API_KEY, ou crie um arquivo .env")
        return False
    return True

def api_request(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Faz uma requisição para a API TESS e retorna a resposta."""
    url = f"{TESS_API_URL}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {TESS_API_KEY}",
        "Content-Type": "application/json"
    }
    
    if DEBUG:
        print(f"\n[DEBUG] Request: {method} {url}")
        if data:
            print(f"[DEBUG] Data: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Método HTTP não suportado: {method}")
        
        if DEBUG:
            print(f"[DEBUG] Status Code: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro {response.status_code}:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print(response.text)
            return {"error": True, "status_code": response.status_code, "message": response.text}
            
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {str(e)}")
        return {"error": True, "message": str(e)}

def listar_agentes() -> None:
    """Lista todos os agentes disponíveis na API TESS."""
    resultado = api_request("agents")
    
    if "data" in resultado:
        print("\n=== AGENTES TESS DISPONÍVEIS ===\n")
        for agente in resultado["data"]:
            print(f"ID: {agente.get('id')} - {agente.get('name', 'Nome não disponível')}")
            print(f"  Descrição: {agente.get('description', 'Sem descrição')}")
            print(f"  Categoria: {agente.get('category', 'N/A')}")
            print()
        
        print(f"Total: {len(resultado['data'])} agentes encontrados")
    else:
        print("Não foi possível obter a lista de agentes.")

def obter_info_agente(agent_id: int) -> None:
    """Obtém informações detalhadas sobre um agente específico."""
    resultado = api_request(f"agents/{agent_id}")
    
    if "error" in resultado:
        print(f"Erro ao obter informações do agente {agent_id}")
        return
    
    print(f"\n=== INFORMAÇÕES DO AGENTE #{agent_id} ===\n")
    print(f"Nome: {resultado.get('name', 'N/A')}")
    print(f"Descrição: {resultado.get('description', 'N/A')}")
    print(f"Categoria: {resultado.get('category', 'N/A')}")
    
    print("\nParâmetros necessários:")
    if "questions" in resultado:
        for param in resultado["questions"]:
            required = "* Obrigatório" if param.get("required", False) else "  Opcional"
            print(f"- {param.get('name')}: {param.get('description')} [{param.get('type')}] {required}")
    else:
        print("Nenhum parâmetro encontrado.")
    
    if "schema" in resultado:
        print("\nSchema de validação:")
        print(json.dumps(resultado["schema"], indent=2, ensure_ascii=False))

def carregar_parametros_arquivo(arquivo: str) -> Dict:
    """Carrega parâmetros de um arquivo JSON."""
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar o arquivo de parâmetros: {str(e)}")
        sys.exit(1)

def formatar_saida_anuncios(output: str) -> None:
    """Formata a saída de anúncios para melhor visualização."""
    print("\n=== ANÚNCIOS GERADOS ===\n")
    
    # Tenta extrair seções de títulos e descrições
    titulos_section = output.split("### Opções de Título:")[1].split("### Opções de Descrição:")[0] if "### Opções de Título:" in output else output
    descricoes_section = output.split("### Opções de Descrição:")[1] if "### Opções de Descrição:" in output else ""
    
    # Títulos
    print("=== TÍTULOS ===")
    for line in titulos_section.strip().split('\n'):
        if line.strip() and not line.startswith("**") and not line == "":
            print(line)
    
    # Descrições
    if descricoes_section:
        print("\n=== DESCRIÇÕES ===")
        for line in descricoes_section.strip().split('\n'):
            if line.strip() and not line == "":
                print(line)

def executar_agente(agent_id: int, args) -> None:
    """Executa um agente TESS com os parâmetros fornecidos."""
    # Inicializa o payload com parâmetros padrão
    payload = {
        'temperature': args.temperature,
        'model': args.model,
        'maxlength': args.maxlength,
        'language': args.language,
        'waitExecution': True
    }
    
    # Adiciona extended_thinking para modelos Claude 3.7 se especificado
    if hasattr(args, 'extended_thinking') and args.extended_thinking and "claude-3-7" in args.model:
        payload['extended_thinking'] = True
        print(f"Usando 'Extended Thinking' com o modelo {args.model} para raciocínio avançado")
    elif "claude-3-7" in args.model:
        print(f"AVISO: O modelo {args.model} parece não estar disponível na API TESS. Considere usar um modelo disponível como 'claude-3-5-sonnet-20240620'.")
    
    # Se fornecido arquivo de parâmetros, carrega dele
    if args.parametros:
        parametros_arquivo = carregar_parametros_arquivo(args.parametros)
        payload.update(parametros_arquivo)
    
    # Adiciona todos os parâmetros passados pela linha de comando
    for param in vars(args):
        if param.startswith("_"):
            continue
        
        # Pula parâmetros que não são para a API
        if param in ["comando", "id", "parametros", "formato_saida", "extended_thinking"]:
            continue
            
        # Só adiciona se o valor foi fornecido pelo usuário
        value = getattr(args, param)
        if value is not None and param.replace("_", "-") not in payload:
            payload[param.replace("_", "-")] = value
    
    # Executa o agente
    resultado = api_request(f"agents/{agent_id}/execute", method="POST", data=payload)
    
    if "error" in resultado:
        print(f"Erro ao executar o agente {agent_id}")
        return
    
    # Processa o resultado
    if "responses" in resultado and len(resultado["responses"]) > 0:
        output = resultado["responses"][0].get("output", "")
        
        if args.formato_saida == "json":
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
        elif args.formato_saida == "formatado" and "anúncios" in output.lower():
            formatar_saida_anuncios(output)
        else:
            print("\n=== RESULTADO ===\n")
            print(output)
    else:
        print("Não foi possível obter resposta do agente.")

def listar_modelos(agent_id: int) -> None:
    """Lista todos os modelos disponíveis na API TESS."""
    resultado = api_request(f"agents/{agent_id}")
    
    if "error" in resultado:
        print(f"Erro ao obter informações do agente {agent_id}")
        return
    
    print("\n=== MODELOS DISPONÍVEIS NA API TESS ===\n")
    
    # Modelos recomendados
    recomendados = [
        {
            "nome": "GPT-4o",
            "valor": "gpt-4o",
            "desc": "Versão avançada do GPT-4 com recursos multimodais - Recomendado"
        },
        {
            "nome": "Claude 3.5 Sonnet",
            "valor": "claude-3-5-sonnet-20240620",
            "desc": "Modelo com bom balanceamento entre velocidade e qualidade"
        },
        {
            "nome": "GPT-4o mini",
            "valor": "gpt-4o-mini",
            "desc": "Versão mais rápida e econômica do GPT-4o"
        }
    ]
    
    # Exibe os modelos recomendados primeiro
    print("MODELOS RECOMENDADOS:")
    for i, modelo in enumerate(recomendados, 1):
        print(f"★ {i}. {modelo['nome']} (valor: {modelo['valor']})")
        print(f"   {modelo['desc']}")
        if "claude-3-7" in modelo['valor']:
            print(f"   *** RECOMENDADO: Melhor modelo com Extended Thinking ***")
    print()
    
    if "questions" in resultado:
        model_param = None
        for param in resultado["questions"]:
            if param.get("name") == "model":
                model_param = param
                break
        
        if model_param and "values" in model_param:
            # Alguns agentes usam "values" em vez de "options"
            options = model_param["values"]
            print("TODOS OS MODELOS DISPONÍVEIS:")
            for i, option in enumerate(options, 1):
                # Se for uma string simples
                if isinstance(option, str):
                    valor = option
                    print(f"{i}. {valor}")
                # Se for um objeto com chaves value/label
                elif isinstance(option, dict):
                    valor = option.get("value", "N/A")
                    label = option.get("label", valor)
                    print(f"{i}. {label} (valor: {valor})")
                
                # Destacar o Claude 3.7 Sonnet se estiver disponível
                if isinstance(option, str) and "claude" in option.lower() and "3.7" in option and "sonnet" in option.lower():
                    print(f"   *** MELHOR ESCOLHA: {option} - Com recurso de Extended Thinking ***")
                elif isinstance(option, dict) and "value" in option:
                    valor = option["value"]
                    if "claude" in valor.lower() and "3.7" in valor and "sonnet" in valor.lower():
                        print(f"   *** MELHOR ESCOLHA: {valor} - Com recurso de Extended Thinking ***")
            
            print(f"\nTotal: {len(options)} modelos encontrados")
        elif model_param and "options" in model_param:
            # Alguns agentes usam "options" em vez de "values"
            options = model_param["options"]
            print("TODOS OS MODELOS DISPONÍVEIS:")
            for i, option in enumerate(options, 1):
                # Se for uma string simples
                if isinstance(option, str):
                    valor = option
                    print(f"{i}. {valor}")
                # Se for um objeto com chaves value/label
                elif isinstance(option, dict):
                    valor = option.get("value", "N/A")
                    label = option.get("label", valor)
                    print(f"{i}. {label} (valor: {valor})")
                
                # Destacar o Claude 3.7 Sonnet se estiver disponível
                if isinstance(option, str) and "claude" in option.lower() and "3.7" in option and "sonnet" in option.lower():
                    print(f"   *** MELHOR ESCOLHA: {option} - Com recurso de Extended Thinking ***")
                elif isinstance(option, dict) and "value" in option:
                    valor = option["value"]
                    if "claude" in valor.lower() and "3.7" in valor and "sonnet" in valor.lower():
                        print(f"   *** MELHOR ESCOLHA: {valor} - Com recurso de Extended Thinking ***")
            
            print(f"\nTotal: {len(options)} modelos encontrados")
        else:
            # Se a estrutura for diferente, tentamos buscar o valor diretamente no schema
            # ou exibimos uma mensagem para testar com outro agente
            print("Informações sobre modelos não encontradas no formato esperado.")
            print("Vamos tentar extrair do schema...")
            
            if "schema" in resultado and "properties" in resultado["schema"]:
                schema_props = resultado["schema"]["properties"]
                if "model" in schema_props and "enum" in schema_props["model"]:
                    models = schema_props["model"]["enum"]
                    print("TODOS OS MODELOS DISPONÍVEIS:")
                    for i, model in enumerate(models, 1):
                        print(f"{i}. {model}")
                        if "claude" in model.lower() and "3.7" in model and "sonnet" in model.lower():
                            print(f"   *** MELHOR ESCOLHA: {model} - Com recurso de Extended Thinking ***")
                    
                    print(f"\nTotal: {len(models)} modelos encontrados")
                else:
                    print("Nenhuma informação de modelos encontrada no schema.")
                    print("Tente outro ID de agente com o parâmetro --agent_id")
            else:
                print("Tente outro ID de agente com o parâmetro --agent_id")
    else:
        print("Nenhuma informação de parâmetros encontrada para este agente.")
        print("Vamos imprimir o objeto completo para análise:")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    
    print("\nPara usar um modelo específico, adicione o parâmetro --model ao executar um agente:")
    print("./tess_api_cli.py executar 45 --model \"gpt-4o\" ...")
    print("\nPara modelos Claude 3.7, você pode usar a função de Extended Thinking:")
    print("./tess_api_cli.py executar 45 --model \"claude-3-5-sonnet-20240620\" --extended_thinking True ...")

def main():
    parser = setup_argparse()
    args = parser.parse_args()
    
    if not check_api_key():
        sys.exit(1)
        
    if args.comando == "listar":
        listar_agentes()
    elif args.comando == "info":
        obter_info_agente(args.id)
    elif args.comando == "modelos":
        listar_modelos(args.agent_id if hasattr(args, 'agent_id') else 45)
    elif args.comando == "executar":
        executar_agente(args.id, args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 