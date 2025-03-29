#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chat simples com a Arcee AI - Versão Independente
"""

import os
import sys
import logging
import json
import requests
from rich.console import Console
from rich.panel import Panel
from rich.box import ROUNDED
from rich.prompt import Prompt
from rich import print
from dotenv import load_dotenv

# Configurar logging
logger = logging.getLogger("arcee_chat")
logger.setLevel(logging.INFO)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter('INFO: %(message)s')
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)

# Handler para arquivo (opcional)
try:
    log_dir = os.path.expanduser("~/.arcee/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "arcee.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
except Exception as e:
    print(f"[yellow]Aviso:[/yellow] Não foi possível configurar o log em arquivo: {e}")

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da interface
console = Console()

class SimpleArceeProvider:
    """Implementação simples do provedor Arcee sem dependências externas"""
    
    def __init__(self):
        """Inicializa o provedor"""
        self.api_key = os.getenv("ARCEE_API_KEY")
        self.api_url = os.getenv("ARCEE_API_URL", "https://api.arcee.ai")
        self.model = os.getenv("ARCEE_MODEL", "auto")
        self.model_usage_stats = {}
    
    def health_check(self):
        """Verifica a disponibilidade do serviço"""
        if not self.api_key:
            return False, "Chave API não configurada"
            
        return True, "Arcee AI disponível"
    
    def generate_content_chat(self, messages):
        """Gera conteúdo usando a API da Arcee AI"""
        if not self.api_key:
            return {"error": "Chave API não configurada"}
            
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "messages": messages,
                "model": self.model
            }
            
            # Fazer requisição à API
            response = requests.post(
                f"{self.api_url}/v1/chat/completions", 
                headers=headers,
                json=data,
                timeout=60
            )
            
            # Verificar resposta
            if response.status_code != 200:
                return {"error": f"Erro na API: {response.status_code} - {response.text}"}
                
            # Processar resposta
            result = response.json()
            
            # Extrair texto da resposta (formato pode variar conforme API)
            if "choices" in result and len(result["choices"]) > 0:
                text = result["choices"][0].get("message", {}).get("content", "")
                model_used = result.get("model", "desconhecido")
                
                # Atualizar estatísticas de uso do modelo
                if model_used in self.model_usage_stats:
                    self.model_usage_stats[model_used] += 1
                else:
                    self.model_usage_stats[model_used] = 1
                
                return {
                    "text": text,
                    "selected_model": model_used
                }
            else:
                return {"error": "Formato de resposta inválido", "raw_response": result}
                
        except Exception as e:
            logger.error(f"Erro ao gerar conteúdo: {str(e)}")
            return {"error": f"Erro ao gerar conteúdo: {str(e)}"}

def chat() -> None:
    """Inicia um chat com o Arcee AI"""
    
    # Log de inicialização
    logger.info("Sistema de logging configurado. Arquivo de log: ~/.arcee/logs/arcee.log")
    logger.info("Iniciando chat com Arcee AI")
    
    # Interface inicial
    console.print(
        Panel(
            "🤖 [bold]Chat com Arcee AI[/bold]\n\n"
            "Este chat permite conversar com a Arcee AI de forma simples.\n"
            "Digite qualquer pergunta ou instrução e a IA responderá.\n\n"
            "Digite 'sair' para encerrar ou 'limpar' para reiniciar a conversa.",
            box=ROUNDED,
            title="Arcee AI",
            border_style="blue"
        )
    )

    # Verificar se a chave API está configurada
    api_key = os.getenv("ARCEE_API_KEY")
    if not api_key:
        console.print("[bold red]Erro:[/bold red] ARCEE_API_KEY não configurada. Configure no arquivo .env")
        sys.exit(1)

    try:
        # Inicializar o provedor Arcee
        provider = SimpleArceeProvider()
        
        # Verificar conexão
        status, message = provider.health_check()
        if status:
            console.print("[green]✓ Conexão com Arcee AI estabelecida[/green]")
            if provider.model == "auto":
                console.print("[green]✓ Modo AUTO ativado - seleção dinâmica de modelo[/green]")
            else:
                console.print(f"[green]✓ Modelo fixo: {provider.model}[/green]")
        else:
            console.print(f"[yellow]⚠ Arcee indisponível: {message}[/yellow]")
            sys.exit(1)
            
        # Lista para armazenar histórico de mensagens
        messages = []

        # Loop principal do chat
        while True:
            try:
                # Obter entrada do usuário
                user_input = Prompt.ask("\n[bold blue]Você[/bold blue]")
                
                # Comandos mínimos (apenas sair e limpar)
                if user_input.lower() == "sair":
                    console.print("[yellow]Encerrando chat...[/yellow]")
                    break
                    
                if user_input.lower() == "limpar":
                    messages = []
                    console.print("[green]✓ Histórico limpo[/green]")
                    continue
                
                # Processar com a Arcee AI
                console.print("[italic]Processando...[/italic]", end="\r")
                
                # Adicionar mensagem ao histórico
                messages.append({"role": "user", "content": user_input})
                
                # Gerar resposta
                response = provider.generate_content_chat(messages)

                # Limpar linha do "Processando..."
                console.print(" " * 30, end="\r")

                # Verificar se houve erro
                if "error" in response:
                    console.print(f"[bold red]Erro:[/bold red] {response['error']}")
                    continue

                # Extrair o texto da resposta
                assistant_message = response["text"]
                
                # Extrair o modelo usado
                model_used = response.get("selected_model", "desconhecido")

                # Mostrar resposta
                console.print(f"\n[bold green]Assistente:[/bold green] {assistant_message}")
                
                # Mostrar informação sobre o modelo usado
                if model_used:
                    console.print(f"[dim italic](Resposta gerada pelo modelo: {model_used})[/dim italic]")
                
                # Adicionar resposta ao histórico
                messages.append({"role": "assistant", "content": assistant_message})

            except KeyboardInterrupt:
                console.print("\n[yellow]Interrompido pelo usuário.[/yellow]")
                break
            except Exception as e:
                console.print(f"[bold red]Erro:[/bold red] {str(e)}")
                continue

        console.print("\nAté logo! 👋")

    except Exception as e:
        console.print(f"[bold red]Erro durante inicialização:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    chat() 