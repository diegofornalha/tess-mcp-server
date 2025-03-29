#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para migrar automaticamente o código para usar o registro centralizado de ferramentas.

Este script complementa o 'find_tools_usage.py', realizando a migração automática
do código que usa ferramentas diretamente de 'src/tools' ou 'tools/' para usar o
novo registro centralizado em 'tools.registry'.
"""

import os
import re
import sys
import argparse
from typing import List, Dict, Tuple, Any
import logging
import json
import shutil
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("migrate_tools")

# Mapeamento de importações para substituição
IMPORT_REPLACEMENTS = {
    # src/tools -> tools.registry
    r"from\s+src\.tools\.mcpx_simple\s+import\s+MCPRunClient": "from tools.registry import get_mcp_client",
    r"from\s+src\.tools\.mcp_nl_processor\s+import\s+MCPNLProcessor": "from tools.registry import get_nl_processor",
    
    # tools -> tools.registry
    r"from\s+tools\.mcpx_simple\s+import\s+MCPRunClient": "from tools.registry import get_mcp_client",
    r"from\s+tools\.tess_nl_processor\s+import\s+TessNLProcessor": "from tools.registry import get_nl_processor",
    r"from\s+tools\.mcpx_tools\s+import\s+get_mcprun_tools": "from tools.registry import get_mcprun_tools",
}

# Mapeamento de uso para substituição
CODE_REPLACEMENTS = {
    # Substituição para instanciação
    r"MCPRunClient\(([^)]*)\)": r"get_mcp_client(\1)",
    r"TessNLProcessor\(([^)]*)\)": r"get_nl_processor(\1)",
    
    # Em caso de importação com alias, tentar substituir
    r"([a-zA-Z0-9_]+)\s*=\s*MCPRunClient\(([^)]*)\)": r"\1 = get_mcp_client(\2)",
    r"([a-zA-Z0-9_]+)\s*=\s*TessNLProcessor\(([^)]*)\)": r"\1 = get_nl_processor(\2)",
}

def find_python_files(root_dir: str, exclude_dirs: List[str] = None) -> List[str]:
    """
    Encontra todos os arquivos Python em um diretório e seus subdiretórios.
    
    Args:
        root_dir: Diretório raiz para busca
        exclude_dirs: Lista de diretórios a serem excluídos da busca
        
    Returns:
        Lista de caminhos de arquivos Python
    """
    if exclude_dirs is None:
        exclude_dirs = ["venv", ".git", "__pycache__", "tools", "src/tools"]
        
    # Normalizar caminhos de exclusão
    exclude_dirs = [os.path.normpath(os.path.join(root_dir, d)) for d in exclude_dirs]
    
    python_files = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Verificar se o diretório atual deve ser excluído
        current_path = os.path.normpath(dirpath)
        if any(current_path.startswith(excluded) for excluded in exclude_dirs):
            continue
            
        # Adicionar arquivos Python
        for filename in filenames:
            if filename.endswith('.py'):
                python_files.append(os.path.join(dirpath, filename))
                
    logger.info(f"Encontrados {len(python_files)} arquivos Python para análise")
    return python_files

def backup_file(filepath: str) -> str:
    """
    Cria um backup do arquivo antes da migração.
    
    Args:
        filepath: Caminho do arquivo a ser copiado
        
    Returns:
        Caminho do arquivo de backup
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}.{timestamp}.bak"
    shutil.copy2(filepath, backup_path)
    return backup_path

def migrate_file(filepath: str, dry_run: bool = False) -> Dict[str, Any]:
    """
    Migra um arquivo Python, substituindo importações e uso direto por chamadas ao registro.
    
    Args:
        filepath: Caminho do arquivo a ser migrado
        dry_run: Se True, apenas simula a migração sem alterar o arquivo
        
    Returns:
        Dicionário com resultados da migração
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # Substituir importações
        for pattern, replacement in IMPORT_REPLACEMENTS.items():
            if re.search(pattern, content):
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    changes_made.append(f"Substituída importação: {pattern} -> {replacement}")
                    content = new_content
        
        # Substituir uso de código
        for pattern, replacement in CODE_REPLACEMENTS.items():
            if re.search(pattern, content):
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    changes_made.append(f"Substituído uso: {pattern} -> {replacement}")
                    content = new_content
        
        # Verificar se houve alterações
        if content != original_content:
            if not dry_run:
                # Fazer backup antes de alterar
                backup_path = backup_file(filepath)
                logger.info(f"Backup criado: {backup_path}")
                
                # Escrever conteúdo modificado
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                logger.info(f"Arquivo migrado: {filepath}")
            else:
                logger.info(f"[DRY RUN] Alterações simuladas para: {filepath}")
                
            return {
                "file": filepath,
                "changes": changes_made,
                "status": "migrated" if not dry_run else "would_migrate"
            }
        else:
            logger.debug(f"Nenhuma alteração necessária para: {filepath}")
            return {
                "file": filepath,
                "changes": [],
                "status": "unchanged"
            }
    except Exception as e:
        logger.error(f"Erro ao migrar arquivo {filepath}: {str(e)}")
        return {
            "file": filepath,
            "changes": [],
            "status": "error",
            "error": str(e)
        }

def main():
    """Função principal para migração de ferramentas"""
    parser = argparse.ArgumentParser(
        description='Migra código para usar o registro centralizado de ferramentas'
    )
    parser.add_argument(
        '--root-dir', 
        default='.',
        help='Diretório raiz do projeto (padrão: diretório atual)'
    )
    parser.add_argument(
        '--exclude-dirs', 
        nargs='+', 
        default=["venv", ".git", "__pycache__", "tools", "src/tools"],
        help='Diretórios a serem excluídos da busca'
    )
    parser.add_argument(
        '--output', 
        help='Arquivo para salvar o relatório de migração em formato JSON'
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Executa sem fazer alterações reais (simulação)'
    )
    args = parser.parse_args()
    
    logger.info(f"Iniciando migração de ferramentas em: {args.root_dir}")
    logger.info(f"Modo: {'Simulação' if args.dry_run else 'Efetivo'}")
    
    # Encontrar arquivos Python
    python_files = find_python_files(args.root_dir, args.exclude_dirs)
    
    # Realizar migração
    results = []
    for filepath in python_files:
        result = migrate_file(filepath, args.dry_run)
        if result["status"] != "unchanged":
            results.append(result)
    
    # Gerar estatísticas
    migrated = len([r for r in results if r["status"] == "migrated"])
    would_migrate = len([r for r in results if r["status"] == "would_migrate"])
    errors = len([r for r in results if r["status"] == "error"])
    
    logger.info(f"\nMigração concluída:")
    logger.info(f"  - Arquivos analisados: {len(python_files)}")
    if args.dry_run:
        logger.info(f"  - Arquivos que seriam migrados: {would_migrate}")
    else:
        logger.info(f"  - Arquivos migrados: {migrated}")
    logger.info(f"  - Erros: {errors}")
    
    # Salvar relatório se solicitado
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": {
                    "files_analyzed": len(python_files),
                    "files_migrated": migrated if not args.dry_run else would_migrate,
                    "errors": errors,
                    "dry_run": args.dry_run
                },
                "results": results
            }, f, indent=2)
        logger.info(f"Relatório salvo em: {args.output}")
    
    if errors > 0:
        logger.warning("Alguns arquivos não puderam ser migrados. Verifique o log para detalhes.")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 