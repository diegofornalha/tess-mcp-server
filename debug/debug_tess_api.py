#!/usr/bin/env python3
"""
Script para testar diretamente a API TESS e o comando listar_agentes
com diferentes parâmetros e filtros.
"""

import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("debug_tess_api")

# Adicionar raiz do projeto ao PATH
project_root = str(Path(__file__).resolve().parent)
sys.path.insert(0, project_root)

try:
    # Importar a função diretamente do módulo
    from tests.test_api_tess import listar_agentes, executar_agente
    
    # Definir comandos para testar
    comandos = [
        ("listar todos os agentes", None, None),
        ("listar agentes tipo chat", "chat", None),
        ("listar agentes tipo text", "text", None),
        ("listar agentes contendo IA", None, "IA"),
    ]
    
    # Executar cada comando e mostrar resultados
    for descricao, tipo, keyword in comandos:
        logger.info(f"Testando: {descricao}")
        print(f"\n=== TESTANDO: {descricao.upper()} ===")
        
        # Chamar a função com os parâmetros apropriados
        success, data = listar_agentes(is_cli=False, filter_type=tipo, keyword=keyword)
        
        if success:
            total = len(data.get('data', []))
            print(f"✅ Sucesso! Encontrados {total} agentes")
            
            # Exibir os primeiros 5 resultados
            for i, agente in enumerate(data.get('data', [])[:5], 1):
                tipo_agente = agente.get('type', 'desconhecido')
                print(f"{i}. {agente.get('title', 'Sem título')} [{tipo_agente}]")
                print(f"   ID: {agente.get('id', 'N/A')}")
                print(f"   Slug: {agente.get('slug', 'N/A')}")
            
            if total > 5:
                print(f"... e mais {total - 5} agentes")
        else:
            print(f"❌ Falha: {data.get('error', 'Erro desconhecido')}")
        
        print("=" * 50)
    
    print("\nTodos os testes concluídos!")
    
except Exception as e:
    logger.error(f"Erro ao executar testes: {e}")
    import traceback
    traceback.print_exc() 