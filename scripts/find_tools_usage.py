#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para encontrar usos diretos de ferramentas que deveriam usar o registro centralizado.

Este script analisa o código fonte do projeto crew_ai_tess_pareto
e identifica importações diretas das ferramentas duplicadas entre 'src/tools' e 'tools/',
sugerindo a migração para o novo registro centralizado.
"""

import os
import re
import sys
import argparse
from typing import List, Dict, Tuple, Any
import logging
import json

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("find_tools_usage")

# Padrões de importação a serem detectados
IMPORT_PATTERNS = {
    # Ferramentas depreciadas (src/tools)
    "src.tools.mcpx_simple": r"from\s+src\.tools\.mcpx_simple\s+import\s+([^\n]+)",
    "src.tools.mcp_nl_processor": r"from\s+src\.tools\.mcp_nl_processor\s+import\s+([^\n]+)",
    
    # Ferramentas recomendadas (tools)
    "tools.mcpx_simple": r"from\s+tools\.mcpx_simple\s+import\s+([^\n]+)",
    "tools.tess_nl_processor": r"from\s+tools\.tess_nl_processor\s+import\s+([^\n]+)",
    "tools.mcpx_tools": r"from\s+tools\.mcpx_tools\s+import\s+([^\n]+)",
}

# Mapeamento para substituições recomendadas
REPLACEMENT_MAP = {
    # src/tools -> tools.registry
    "src.tools.mcpx_simple.MCPRunClient": "tools.registry.get_mcp_client",
    "src.tools.mcp_nl_processor.MCPNLProcessor": "tools.registry.get_nl_processor",
    
    # tools -> tools.registry
    "tools.mcpx_simple.MCPRunClient": "tools.registry.get_mcp_client",
    "tools.tess_nl_processor.TessNLProcessor": "tools.registry.get_nl_processor",
    "tools.mcpx_tools.get_mcprun_tools": "tools.registry.get_mcprun_tools",
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
        exclude_dirs = []
        
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

def analyze_file(filepath: str) -> Dict[str, Any]:
    """
    Analisa um arquivo Python procurando por importações diretas de ferramentas.
    
    Args:
        filepath: Caminho do arquivo a ser analisado
        
    Returns:
        Dicionário com resultados da análise
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    results = {
        "file": filepath,
        "imports": {},
        "suggested_changes": []
    }
    
    # Procurar por cada padrão de importação
    for module, pattern in IMPORT_PATTERNS.items():
        matches = re.findall(pattern, content)
        if matches:
            imports = []
            for match in matches:
                # Separar múltiplas importações em uma linha (e.g., "Class1, Class2")
                for item in match.split(','):
                    item = item.strip()
                    if item:
                        imports.append(item)
                        
            if imports:
                results["imports"][module] = imports
                
                # Gerar sugestões de mudança
                for imported_item in imports:
                    full_import = f"{module}.{imported_item}"
                    if full_import in REPLACEMENT_MAP:
                        replacement = REPLACEMENT_MAP[full_import]
                        results["suggested_changes"].append({
                            "original": full_import,
                            "suggested": replacement,
                            "line_examples": find_usage_examples(content, imported_item)
                        })
    
    return results

def find_usage_examples(content: str, imported_name: str, max_examples: int = 3) -> List[str]:
    """
    Encontra exemplos de uso de um item importado no conteúdo do arquivo.
    
    Args:
        content: Conteúdo do arquivo
        imported_name: Nome do item importado
        max_examples: Número máximo de exemplos a retornar
        
    Returns:
        Lista de linhas contendo exemplos de uso
    """
    # Padrão para variáveis, instanciação direta, chamadas de função, etc.
    patterns = [
        rf"{imported_name}\s*\(",  # Instanciação ou chamada de função
        rf"=\s*{imported_name}",   # Atribuição
        rf":\s*{imported_name}",   # Anotação de tipo
    ]
    
    examples = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        for pattern in patterns:
            if re.search(pattern, line) and len(examples) < max_examples:
                line_number = i + 1
                examples.append(f"Linha {line_number}: {line.strip()}")
                break
                
    return examples

def generate_migration_suggestions(analysis_results: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Gera sugestões de migração a partir dos resultados da análise.
    
    Args:
        analysis_results: Resultados da análise por arquivo
        
    Returns:
        Lista de sugestões de migração
    """
    suggestions = []
    
    for filepath, result in analysis_results.items():
        if result["suggested_changes"]:
            file_suggestions = {
                "file": filepath,
                "suggested_changes": result["suggested_changes"],
                "migration_example": generate_migration_example(result)
            }
            suggestions.append(file_suggestions)
            
    return suggestions

def generate_migration_example(file_result: Dict[str, Any]) -> Dict[str, str]:
    """
    Gera exemplos de migração para um arquivo.
    
    Args:
        file_result: Resultado da análise de um arquivo
        
    Returns:
        Dicionário com exemplos "antes" e "depois"
    """
    before_lines = []
    after_lines = []
    
    # Gerar importações "antes"
    for module, imports in file_result["imports"].items():
        before_lines.append(f"from {module} import {', '.join(imports)}")
    
    # Gerar importações "depois"
    registry_imports = set()
    direct_imports = set()
    
    for change in file_result["suggested_changes"]:
        parts = change["suggested"].split('.')
        if parts[-2] == "registry":
            # Importação do registro
            registry_imports.add(parts[-1])
        else:
            # Importação direta
            module = '.'.join(parts[:-1])
            item = parts[-1]
            direct_imports.add((module, item))
    
    if registry_imports:
        after_lines.append(f"from tools.registry import {', '.join(sorted(registry_imports))}")
        
    for module, item in sorted(direct_imports):
        after_lines.append(f"from {module} import {item}")
        
    # Gerar exemplos de uso "antes" e "depois"
    usage_examples = []
    for change in file_result["suggested_changes"]:
        if change["line_examples"]:
            for example in change["line_examples"]:
                # Extrair apenas o código, sem o número da linha
                if ': ' in example:
                    code = example.split(': ', 1)[1]
                    usage_examples.append({
                        "before": code,
                        "after": code.replace(
                            change["original"].split('.')[-1],
                            change["suggested"].split('.')[-1] + "()"
                        )
                    })
    
    return {
        "imports": {
            "before": '\n'.join(before_lines),
            "after": '\n'.join(after_lines)
        },
        "usage_examples": usage_examples
    }

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Encontra usos diretos de ferramentas que deveriam usar o registro centralizado'
    )
    parser.add_argument(
        '--root-dir', '-r',
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
        help='Diretório raiz para busca (padrão: raiz do projeto)'
    )
    parser.add_argument(
        '--exclude-dirs', '-e',
        nargs='+',
        default=['venv', 'env', '.env', '.venv', 'tests', 'tools'],
        help='Diretórios a serem excluídos da busca'
    )
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Arquivo para salvar resultados em JSON (opcional)'
    )
    
    args = parser.parse_args()
    
    # Encontrar arquivos Python
    python_files = find_python_files(args.root_dir, args.exclude_dirs)
    
    # Analisar cada arquivo
    analysis_results = {}
    for filepath in python_files:
        result = analyze_file(filepath)
        if result["imports"]:
            rel_path = os.path.relpath(filepath, args.root_dir)
            analysis_results[rel_path] = result
            
    # Gerar sugestões de migração
    migration_suggestions = generate_migration_suggestions(analysis_results)
    
    # Exibir resultados
    if migration_suggestions:
        logger.info(f"Encontrados {len(migration_suggestions)} arquivos com uso direto de ferramentas")
        
        for suggestion in migration_suggestions:
            filepath = suggestion["file"]
            changes = suggestion["suggested_changes"]
            example = suggestion["migration_example"]
            
            logger.info(f"\nArquivo: {filepath}")
            logger.info(f"Número de alterações sugeridas: {len(changes)}")
            
            logger.info("\nImportações:")
            logger.info("Antes:")
            logger.info(example["imports"]["before"])
            logger.info("\nDepois:")
            logger.info(example["imports"]["after"])
            
            if example["usage_examples"]:
                logger.info("\nExemplos de uso:")
                for idx, usage in enumerate(example["usage_examples"]):
                    logger.info(f"Exemplo {idx + 1}:")
                    logger.info(f"Antes: {usage['before']}")
                    logger.info(f"Depois: {usage['after']}")
            
            logger.info("-" * 80)
    else:
        logger.info("Nenhum uso direto de ferramentas encontrado!")
    
    # Salvar resultados em arquivo se solicitado
    if args.output and migration_suggestions:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump({
                "analysis_summary": {
                    "files_analyzed": len(python_files),
                    "files_with_direct_imports": len(migration_suggestions)
                },
                "migration_suggestions": migration_suggestions
            }, f, indent=2)
        logger.info(f"Resultados salvos em {args.output}")

if __name__ == "__main__":
    main() 