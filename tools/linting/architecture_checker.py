"""
Checker personalizado para validar a conformidade arquitetural através do Pylint.

Para usar este checker, configure o arquivo .pylintrc:
[MASTER]
load-plugins=tools.linting.architecture_checker
"""

from typing import Any, Dict, List, Optional, Tuple, Set
from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
import astroid
import os
import re

class ArchitectureChecker(BaseChecker):
    """
    Pylint checker para validar conformidade com a arquitetura de referência.
    Verifica principalmente as dependências entre camadas.
    """
    
    __implements__ = IAstroidChecker
    
    name = 'architecture'
    priority = -1
    msgs = {
        'E9001': (
            'Domain layer should not import from %s layer',
            'domain-imports-outer-layer',
            'Domain layer should not depend on infrastructure, application or interface layers'
        ),
        'E9002': (
            'Application layer should not import from %s layer',
            'application-imports-outer-layer',
            'Application layer should only depend on domain layer, not on infrastructure or interfaces'
        ),
        'E9003': (
            'Infrastructure layer should not import from %s layer',
            'infrastructure-imports-interface-layer',
            'Infrastructure layer should not depend on interface layer'
        ),
        'E9004': (
            'Import violates architectural dependency rules: %s imports %s',
            'architectural-dependency-violation',
            'Imports should follow the dependency rules established in architecture reference'
        ),
    }
    
    options = (
        ('architecture-allowed-imports',
         {'default': (), 'type': 'csv',
          'metavar': '<module names>',
          'help': 'List of architectural exceptions (imports that are allowed despite violating the rules)'}
        ),
    )
    
    def __init__(self, linter=None):
        super().__init__(linter)
        self.allowed_imports = set()
        
    def open(self):
        """Initialize checker."""
        self.allowed_imports = set(self.config.architecture_allowed_imports)
    
    def _get_current_layer(self, path: str) -> str:
        """
        Determina a camada arquitetural do arquivo atual.
        
        Args:
            path: Caminho do arquivo
            
        Returns:
            str: Nome da camada ('domain', 'application', 'infrastructure', 'interfaces', etc.)
        """
        if not path:
            return 'unknown'
            
        if 'domain/' in path or path.startswith('domain/'):
            return 'domain'
            
        if 'application/' in path or path.startswith('application/'):
            return 'application'
            
        if 'infrastructure/' in path or path.startswith('infrastructure/'):
            return 'infrastructure'
            
        if 'interfaces/' in path or path.startswith('interfaces/'):
            return 'interfaces'
            
        return 'other'
    
    def _get_import_layer(self, import_name: str) -> str:
        """
        Determina a camada arquitetural do módulo importado.
        
        Args:
            import_name: Nome do módulo importado
            
        Returns:
            str: Nome da camada ('domain', 'application', 'infrastructure', 'interfaces', 'standard_lib', 'external')
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
            
        if '.' not in import_name:
            return 'standard_lib'
            
        return 'external'
    
    def _is_architectural_violation(self, from_layer: str, to_layer: str) -> bool:
        """
        Verifica se a importação viola as regras arquiteturais.
        
        Args:
            from_layer: Camada que está importando
            to_layer: Camada que está sendo importada
            
        Returns:
            bool: True se a importação viola as regras arquiteturais
        """
        # Regra 1: Domain não pode depender de nenhuma outra camada do projeto
        if from_layer == 'domain' and to_layer in ['application', 'infrastructure', 'interfaces', 'src']:
            return True
            
        # Regra 2: Application pode depender apenas de domain
        if from_layer == 'application' and to_layer in ['infrastructure', 'interfaces', 'src']:
            return True
            
        # Regra 3: Infrastructure pode depender de domain e application
        if from_layer == 'infrastructure' and to_layer in ['interfaces']:
            return True
            
        return False
    
    def visit_import(self, node):
        """
        Verifica importações diretas (import xxx).
        
        Args:
            node: Nó AST representando a importação
        """
        current_file = node.root().file
        current_layer = self._get_current_layer(current_file)
        
        for name in node.names:
            import_name = name[0]
            import_layer = self._get_import_layer(import_name)
            
            # Ignorar bibliotecas padrão ou externas
            if import_layer in ['standard_lib', 'external']:
                continue
            
            # Verificar se viola regras arquiteturais
            if self._is_architectural_violation(current_layer, import_layer):
                # Verificar exceções permitidas
                if f"{current_layer}:{import_name}" in self.allowed_imports:
                    continue
                    
                # Adicionar mensagem apropriada
                if current_layer == 'domain':
                    self.add_message('domain-imports-outer-layer', node=node, args=(import_layer,))
                elif current_layer == 'application':
                    self.add_message('application-imports-outer-layer', node=node, args=(import_layer,))
                elif current_layer == 'infrastructure':
                    self.add_message('infrastructure-imports-interface-layer', node=node, args=(import_layer,))
                else:
                    self.add_message('architectural-dependency-violation', node=node, 
                                    args=(current_layer, import_layer))
    
    def visit_importfrom(self, node):
        """
        Verifica importações do tipo 'from xxx import yyy'.
        
        Args:
            node: Nó AST representando a importação
        """
        if not node.modname:
            return
            
        current_file = node.root().file
        current_layer = self._get_current_layer(current_file)
        import_layer = self._get_import_layer(node.modname)
        
        # Ignorar bibliotecas padrão ou externas
        if import_layer in ['standard_lib', 'external']:
            return
        
        # Verificar se viola regras arquiteturais
        if self._is_architectural_violation(current_layer, import_layer):
            # Verificar exceções permitidas
            if f"{current_layer}:{node.modname}" in self.allowed_imports:
                return
                
            # Adicionar mensagem apropriada
            if current_layer == 'domain':
                self.add_message('domain-imports-outer-layer', node=node, args=(import_layer,))
            elif current_layer == 'application':
                self.add_message('application-imports-outer-layer', node=node, args=(import_layer,))
            elif current_layer == 'infrastructure':
                self.add_message('infrastructure-imports-interface-layer', node=node, args=(import_layer,))
            else:
                self.add_message('architectural-dependency-violation', node=node, 
                                args=(current_layer, import_layer))

def register(linter):
    """Registra o checker no Pylint."""
    linter.register_checker(ArchitectureChecker(linter)) 