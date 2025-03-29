#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exemplo de uso do cliente MCP unificado
"""

import os
import sys
import json
from pathlib import Path

# Adicionar diretório raiz ao sys.path
project_root = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(0, project_root)

from infrastructure.mcp_client import MCPClientUnificado

def exemplo_cliente_generico():
    """Exemplo de uso do cliente genérico"""
    print("\n=== Exemplo Cliente Genérico ===")
    cliente = MCPClientUnificado(service_type="generic")
    
    # Listar ferramentas
    print("Listando ferramentas disponíveis...")
    success, tools = cliente.get_tools()
    
    if success:
        print(f"✅ {len(tools)} ferramentas encontradas:")
        for i, tool in enumerate(tools, 1):
            print(f"  {i}. {tool.get('name')} - {tool.get('description', 'Sem descrição')}")
    else:
        print(f"❌ Erro ao listar ferramentas: {tools}")
    
    # Executar uma ferramenta simples
    print("\nExecutando ferramenta 'echo'...")
    success, result = cliente.run_tool("echo", "say", {"message": "Teste do cliente MCP unificado"})
    
    if success:
        print(f"✅ Resultado: {result}")
    else:
        print(f"❌ Erro ao executar ferramenta: {result}")

def exemplo_cliente_veyrax():
    """Exemplo de uso do cliente Veyrax"""
    print("\n=== Exemplo Cliente Veyrax ===")
    cliente = MCPClientUnificado(service_type="veyrax")
    
    # Salvar uma memória
    print("Salvando memória...")
    success, result = cliente.save_memory("Testando o cliente MCP unificado", "example")
    
    if success:
        print(f"✅ Memória salva: {result}")
    else:
        print(f"❌ Erro ao salvar memória: {result}")
    
    # Obter memórias
    print("\nObtendo memórias...")
    success, memories = cliente.get_memories(limit=5)
    
    if success:
        print(f"✅ {len(memories)} memórias encontradas:")
        for i, memory in enumerate(memories, 1):
            print(f"  {i}. {memory.get('content')[:50]}... ({memory.get('tool')})")
    else:
        print(f"❌ Erro ao obter memórias: {memories}")

def exemplo_cliente_mcp_run():
    """Exemplo de uso do cliente MCP.run"""
    print("\n=== Exemplo Cliente MCP.run ===")
    cliente = MCPClientUnificado(service_type="mcp_run")
    
    # Iniciar uma sessão
    print("Iniciando sessão...")
    success, session = cliente.start_session()
    
    if success:
        print(f"✅ Sessão iniciada: {session.get('session_id')}")
    else:
        print(f"❌ Erro ao iniciar sessão: {session}")
        return
    
    # Listar ferramentas disponíveis
    print("\nListando ferramentas disponíveis...")
    success, tools = cliente.get_tools()
    
    if success:
        print(f"✅ {len(tools)} ferramentas encontradas:")
        for i, tool in enumerate(tools, 1):
            print(f"  {i}. {tool.get('name')} - {tool.get('description', 'Sem descrição')}")
    else:
        print(f"❌ Erro ao listar ferramentas: {tools}")

def main():
    """Função principal"""
    print("=== Demonstração do Cliente MCP Unificado ===")
    
    # Executar os exemplos
    try:
        exemplo_cliente_generico()
    except Exception as e:
        print(f"❌ Erro ao executar exemplo do cliente genérico: {e}")
    
    try:
        exemplo_cliente_veyrax()
    except Exception as e:
        print(f"❌ Erro ao executar exemplo do cliente Veyrax: {e}")
    
    try:
        exemplo_cliente_mcp_run()
    except Exception as e:
        print(f"❌ Erro ao executar exemplo do cliente MCP.run: {e}")

if __name__ == "__main__":
    main() 