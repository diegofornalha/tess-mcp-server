#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Implementação do comando de chat interativo
"""

import sys
import logging
from ..utils.logging import get_logger, configure_logging

try:
    from arcee_chat import chat as arcee_chat
except ImportError:
    # Fallback para compatibilidade
    try:
        from crew.arcee_chat import chat as arcee_chat
    except ImportError:
        arcee_chat = None

# Configurar logging
configure_logging()
logger = get_logger(__name__)

def chat_command(modelo="auto"):
    """
    Inicia o chat interativo
    
    Args:
        modelo: Modelo a ser utilizado (default: auto)
    """
    if arcee_chat:
        arcee_chat()
    else:
        print("Erro: Módulo de chat não disponível.")

def main():
    """Função principal que inicia o chat com Arcee AI."""
    try:
        # Executa o chat Arcee com modo AUTO
        chat_command()
    except Exception as e:
        logger.exception(f"Erro durante execução do chat: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 