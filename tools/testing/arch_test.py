"""
Testes para validar a conformidade com a arquitetura de referência.

Este módulo contém testes que verificam se o código-fonte segue
as regras de dependência entre camadas definidas na arquitetura.
"""

import os
import ast
import pytest
from typing import List, Dict, Set, Tuple

def get_imports(file_path: str) -> List[str]:
    """
    Extrai todas as importações de um arquivo Python.
    
    Args:
        file_path: Caminho para o arquivo Python
        
    Returns:
        Lista de nomes de módulos importados
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            tree = ast.parse(file.read())
        except SyntaxError:
            # Ignorar arquivos com erros de sintaxe
            return []
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append(name.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for name in node.names:
                    imports.append(f"{node.module}.{name.name}")
    
    return imports

def get_layer_from_path(file_path: str) -> str:
    """
    Determina a camada arquitetural com base no caminho do arquivo.
    
    Args:
        file_path: Caminho do arquivo
        
    Returns:
        Nome da camada ('domain', 'application', 'infrastructure', 'interfaces', etc.)
    """
    normalized_path = file_path.replace('\\', '/')
    
    if '/domain/' in normalized_path or normalized_path.startswith('domain/'):
        return 'domain'
        
    if '/application/' in normalized_path or normalized_path.startswith('application/'):
        return 'application'
        
    if '/infrastructure/' in normalized_path or normalized_path.startswith('infrastructure/'):
        return 'infrastructure'
        
    if '/interfaces/' in normalized_path or normalized_path.startswith('interfaces/'):
        return 'interfaces'
        
    return 'other'

def get_layer_from_import(import_name: str) -> str:
    """
    Determina a camada arquitetural com base no nome do módulo importado.
    
    Args:
        import_name: Nome do módulo importado
        
    Returns:
        Nome da camada
    """
    if import_name.startswith('domain.'):
        return 'domain'
        
    if import_name.startswith('application.'):
        return 'application'
        
    if import_name.startswith('infrastructure.'):
        return 'infrastructure'
        
    if import_name.startswith('interfaces.'):
        return 'interfaces'
        
    if import_name.startswith('src.'):
        return 'src'
        
    if import_name.startswith('tools.'):
        return 'tools'
        
    return 'external'

def is_violation(from_layer: str, to_layer: str) -> bool:
    """
    Verifica se uma importação de uma camada para outra viola as regras arquiteturais.
    
    Args:
        from_layer: Camada que está importando
        to_layer: Camada que está sendo importada
        
    Returns:
        True se a importação viola as regras, False caso contrário
    """
    # Se ambas as camadas são externas ou a mesma, não é violação
    if from_layer == 'external' or to_layer == 'external' or from_layer == to_layer:
        return False
    
    # Regra 1: Domain não pode depender de outras camadas do projeto
    if from_layer == 'domain' and to_layer in ['application', 'infrastructure', 'interfaces', 'src']:
        return True
    
    # Regra 2: Application pode depender apenas de domain
    if from_layer == 'application' and to_layer in ['infrastructure', 'interfaces', 'src']:
        return True
    
    # Regra 3: Infrastructure pode depender apenas de domain e application
    if from_layer == 'infrastructure' and to_layer in ['interfaces']:
        return True
    
    return False

def collect_py_files(base_dir: str) -> List[str]:
    """
    Coleta todos os arquivos Python em um diretório recursivamente.
    
    Args:
        base_dir: Diretório base para busca
        
    Returns:
        Lista de caminhos para arquivos Python
    """
    py_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    
    return py_files

def find_violations() -> Dict[str, List[str]]:
    """
    Encontra todas as violações de dependência entre camadas no projeto.
    
    Returns:
        Dicionário com arquivos como chaves e listas de violações como valores
    """
    violations = {}
    
    # Diretórios a serem verificados
    directories = ['domain', 'application', 'infrastructure', 'interfaces']
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
            
        for file_path in collect_py_files(directory):
            file_layer = get_layer_from_path(file_path)
            imports = get_imports(file_path)
            
            file_violations = []
            for imp in imports:
                imp_layer = get_layer_from_import(imp)
                if is_violation(file_layer, imp_layer):
                    file_violations.append(f"Imports {imp} (layer: {imp_layer})")
            
            if file_violations:
                violations[file_path] = file_violations
    
    return violations

def test_domain_doesnt_import_other_layers():
    """Testa se a camada de domínio não importa de outras camadas."""
    if not os.path.exists('domain'):
        pytest.skip("Domain directory not found")
        
    for file_path in collect_py_files('domain'):
        imports = get_imports(file_path)
        
        for imp in imports:
            imp_layer = get_layer_from_import(imp)
            assert imp_layer not in ['application', 'infrastructure', 'interfaces', 'src'], \
                f"{file_path} imports from {imp_layer} layer: {imp}"

def test_application_imports():
    """Testa se a camada de aplicação importa apenas do domínio."""
    if not os.path.exists('application'):
        pytest.skip("Application directory not found")
        
    for file_path in collect_py_files('application'):
        imports = get_imports(file_path)
        
        for imp in imports:
            imp_layer = get_layer_from_import(imp)
            if imp_layer in ['infrastructure', 'interfaces', 'src']:
                assert False, f"{file_path} imports from {imp_layer} layer: {imp}"

def test_infrastructure_imports():
    """Testa se a camada de infraestrutura não importa da camada de interface."""
    if not os.path.exists('infrastructure'):
        pytest.skip("Infrastructure directory not found")
        
    for file_path in collect_py_files('infrastructure'):
        imports = get_imports(file_path)
        
        for imp in imports:
            imp_layer = get_layer_from_import(imp)
            assert imp_layer != 'interfaces', \
                f"{file_path} imports from interfaces layer: {imp}"

def test_allowed_dependencies():
    """Testa o grafo completo de dependências."""
    violations = find_violations()
    
    # Imprimir todas as violações para facilitar o diagnóstico
    for file, file_violations in violations.items():
        for violation in file_violations:
            print(f"{file}: {violation}")
    
    # Falhar o teste se houver violações
    assert not violations, f"Found {len(violations)} files with architectural violations"

if __name__ == "__main__":
    # Rodar verificação manualmente
    violations = find_violations()
    
    if violations:
        print(f"Found {len(violations)} files with architectural violations:")
        for file, file_violations in violations.items():
            print(f"\n{file}:")
            for violation in file_violations:
                print(f"  - {violation}")
        exit(1)
    else:
        print("No architectural violations found! ✅")
        exit(0) 