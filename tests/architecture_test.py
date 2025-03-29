#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Testes para verificar a conformidade da arquitetura do projeto.

Este módulo verifica se a estrutura do projeto está de acordo com as
regras da Clean Architecture e DDD, garantindo que as dependências
apontem na direção correta (de fora para dentro).
"""

import os
import sys
import unittest
import importlib
import ast
from pathlib import Path


class DependencyChecker(ast.NodeVisitor):
    """
    Verifica as dependências entre módulos através da análise estática.
    """
    
    def __init__(self, filename):
        self.filename = filename
        self.imports = []
        self.from_imports = []
    
    def visit_Import(self, node):
        """Captura imports diretos."""
        for name in node.names:
            self.imports.append(name.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Captura imports com from."""
        if node.module is not None:
            for name in node.names:
                self.from_imports.append(f"{node.module}.{name.name}")
        self.generic_visit(node)


class ArchitectureTest(unittest.TestCase):
    """Testes para verificar a conformidade da arquitetura do projeto."""
    
    def setUp(self):
        """Configura o ambiente para os testes."""
        # Adiciona o diretório raiz ao path para permitir importações
        self.root_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(self.root_dir))
        
        # Mapeia as camadas da arquitetura
        self.layers = {
            "domain": ["domain"],
            "application": ["application"],
            "infrastructure": ["infrastructure"],
            "interface": ["src"]
        }
        
        # Define as regras de dependência (de quem pode depender)
        self.allowed_dependencies = {
            "domain": [],  # Domínio não pode depender de nada
            "application": ["domain"],  # Aplicação pode depender do domínio
            "infrastructure": ["domain", "application"],  # Infraestrutura pode depender do domínio e aplicação
            "interface": ["domain", "application", "infrastructure"]  # Interface pode depender de tudo
        }
    
    def test_domain_has_no_external_dependencies(self):
        """Testa se o domínio não tem dependências externas."""
        violations = self._check_layer_dependencies("domain")
        
        self.assertEqual(len(violations), 0, 
                         f"O domínio não deve ter dependências externas, mas foram encontradas: {violations}")
    
    def test_application_dependencies(self):
        """Testa se a aplicação só depende do domínio."""
        violations = self._check_layer_dependencies("application")
        
        self.assertEqual(len(violations), 0, 
                         f"A aplicação só deve depender do domínio, mas foram encontradas dependências de: {violations}")
    
    def test_infrastructure_dependencies(self):
        """Testa se a infraestrutura só depende do domínio e da aplicação."""
        violations = self._check_layer_dependencies("infrastructure")
        
        self.assertEqual(len(violations), 0, 
                         f"A infraestrutura só deve depender do domínio e da aplicação, mas foram encontradas dependências de: {violations}")
    
    def test_interface_dependencies(self):
        """Testa se a interface só depende de camadas internas."""
        violations = self._check_layer_dependencies("interface")
        
        self.assertEqual(len(violations), 0, 
                         f"A interface só deve depender de camadas internas, mas foram encontradas dependências externas: {violations}")
    
    def _get_layer_for_module(self, module_name):
        """Identifica a qual camada um módulo pertence."""
        for layer, prefixes in self.layers.items():
            for prefix in prefixes:
                if module_name.startswith(prefix):
                    return layer
        return None
    
    def _is_stdlib_module(self, module_name):
        """Verifica se um módulo pertence à biblioteca padrão Python."""
        try:
            # Se o módulo é importável mas não tem __file__, é da stdlib
            module = importlib.import_module(module_name.split('.')[0])
            return not hasattr(module, '__file__') or 'site-packages' not in module.__file__
        except ImportError:
            # Se não conseguir importar o módulo, consideramos como não sendo da stdlib
            return False
    
    def _check_layer_dependencies(self, layer):
        """Verifica as dependências de uma camada."""
        violations = []
        allowed = self.allowed_dependencies[layer]
        
        # Para cada diretório na camada
        for prefix in self.layers[layer]:
            layer_dir = self.root_dir / prefix
            if not layer_dir.exists():
                continue
                
            # Para cada arquivo Python no diretório (recursivamente)
            for file_path in layer_dir.glob("**/*.py"):
                relative_path = file_path.relative_to(self.root_dir)
                
                # Analisa as importações no arquivo
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read(), filename=str(file_path))
                        checker = DependencyChecker(str(file_path))
                        checker.visit(tree)
                        
                        # Verifica se as importações violam as regras
                        for import_name in checker.imports + checker.from_imports:
                            # Ignora imports relativos e da biblioteca padrão
                            if import_name.startswith(".") or self._is_stdlib_module(import_name.split('.')[0]):
                                continue
                                
                            import_layer = self._get_layer_for_module(import_name.split('.')[0])
                            if import_layer and import_layer not in allowed:
                                violations.append(f"{relative_path}: {import_name} (camada {import_layer})")
                    except SyntaxError:
                        print(f"Erro ao analisar o arquivo: {file_path}")
        
        return violations


if __name__ == "__main__":
    unittest.main() 