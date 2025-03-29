#!/usr/bin/env python3
"""
Ponto de entrada principal para a CLI da Arcee/TESS.
Este arquivo inicia a CLI e roteia para os comandos específicos.
"""

import sys
import logging

# Configurar logging
from .utils.logging import configure_logging

# Importar comandos
from .commands.mcp import main_configurar, main_listar, main_executar
from .commands.mcp_tools import (
    main_listar as mcp_tools_listar,
    main_buscar as mcp_tools_buscar,
    main_detalhes as mcp_tools_detalhes,
    main_executar as mcp_tools_executar
)

# Importar o chat Arcee usando caminho absoluto em vez de relativo
try:
    from arcee_chat import chat as arcee_chat
except ImportError:
    # Fallback para compatibilidade
    try:
        from crew.arcee_chat import chat as arcee_chat
    except ImportError:
        arcee_chat = None

# Configurar logging
logger = logging.getLogger('arcee_cli')
configure_logging()

def cli():
    """Função principal da CLI"""
    # Analisar argumentos
    if len(sys.argv) < 2:
        # Se não houver comandos, mostrar ajuda geral
        _mostrar_ajuda_geral()
        return
    
    # Obter comando principal
    comando = sys.argv[1].lower()
    
    # Processar comandos
    if comando == "chat":
        # Iniciar chat interativo com o Arcee AI
        if arcee_chat:
            arcee_chat()
        else:
            logger.error("Módulo de chat não disponível")
    elif comando == "mcp":
        # Processar subcomandos do MCP (legado)
        _processar_mcp_comando()
    elif comando == "mcp-tools":
        # Processar subcomandos de ferramentas MCP (novo)
        _processar_mcp_tools_comando()
    else:
        # Comando desconhecido
        logger.error(f"Comando desconhecido: {comando}")
        _mostrar_ajuda_geral()

def _mostrar_ajuda_geral():
    """Mostra ajuda geral da CLI"""
    print("Uso: arcee <comando> [opções]")
    print("\nComandos disponíveis:")
    print("  chat      - Iniciar chat interativo com o Arcee AI")
    print("  mcp       - Interagir com o MCP (legado)")
    print("  mcp-tools - Gerenciar ferramentas MCP (novo)")
    print("\nPara ajuda específica, use: arcee <comando> --help")

def _processar_mcp_comando():
    """Processa subcomandos do MCP (legado)"""
    if len(sys.argv) < 3:
        # Se não houver subcomandos, mostrar ajuda do MCP
        _mostrar_ajuda_mcp()
        return
    
    # Obter subcomando
    subcomando = sys.argv[2].lower()
    
    if subcomando == "configurar":
        main_configurar()
    elif subcomando == "listar":
        main_listar()
    elif subcomando == "executar":
        if len(sys.argv) < 4:
            logger.error("Nome do agente não especificado")
            return
        
        nome = sys.argv[3]
        params = sys.argv[4] if len(sys.argv) > 4 else None
        
        main_executar(nome, params)
    else:
        logger.error(f"Subcomando MCP desconhecido: {subcomando}")
        _mostrar_ajuda_mcp()

def _processar_mcp_tools_comando():
    """Processa subcomandos de ferramentas MCP (novo)"""
    if len(sys.argv) < 3:
        # Se não houver subcomandos, mostrar ajuda de ferramentas MCP
        _mostrar_ajuda_mcp_tools()
        return
    
    # Obter subcomando
    subcomando = sys.argv[2].lower()
    
    if subcomando == "listar":
        mcp_tools_listar()
    elif subcomando == "buscar":
        if len(sys.argv) < 4:
            logger.error("Texto de busca não especificado")
            print("❌ Uso correto: arcee mcp-tools buscar <texto>")
            return
        
        texto_busca = sys.argv[3]
        mcp_tools_buscar(texto_busca)
    elif subcomando == "detalhes":
        if len(sys.argv) < 4:
            logger.error("ID da ferramenta não especificado")
            print("❌ Uso correto: arcee mcp-tools detalhes <id>")
            return
        
        tool_id = sys.argv[3]
        mcp_tools_detalhes(tool_id)
    elif subcomando == "executar":
        if len(sys.argv) < 4:
            logger.error("ID da ferramenta não especificado")
            print("❌ Uso correto: arcee mcp-tools executar <id> [params]")
            return
        
        tool_id = sys.argv[3]
        params = sys.argv[4] if len(sys.argv) > 4 else None
        
        mcp_tools_executar(tool_id, params)
    else:
        logger.error(f"Subcomando MCP-Tools desconhecido: {subcomando}")
        _mostrar_ajuda_mcp_tools()

def _mostrar_ajuda_mcp():
    """Mostra ajuda específica para comandos MCP (legado)"""
    print("Uso: arcee mcp <subcomando> [opções]")
    print("\nSubcomandos disponíveis:")
    print("  configurar - Configurar ambiente MCP")
    print("  listar     - Listar agentes disponíveis")
    print("  executar   - Executar um agente específico")
    print("\nExemplos:")
    print("  arcee mcp listar")
    print("  arcee mcp executar professional-dev-ai \"Como implementar padrão Strategy?\"")

def _mostrar_ajuda_mcp_tools():
    """Mostra ajuda específica para comandos de ferramentas MCP (novo)"""
    print("Uso: arcee mcp-tools <subcomando> [opções]")
    print("\nSubcomandos disponíveis:")
    print("  listar    - Listar todas as ferramentas disponíveis")
    print("  buscar    - Buscar ferramentas por texto")
    print("  detalhes  - Mostrar detalhes de uma ferramenta específica")
    print("  executar  - Executar uma ferramenta específica")
    print("\nExemplos:")
    print("  arcee mcp-tools listar")
    print("  arcee mcp-tools buscar \"processamento\"")
    print("  arcee mcp-tools detalhes tool1")
    print("  arcee mcp-tools executar tool1 '{\"param1\": \"valor1\"}'")

if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        logger.error(f"Erro ao executar comando: {str(e)}")
        sys.exit(1) 