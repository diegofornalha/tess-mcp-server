"""
Camada de domínio da aplicação.
Contém as regras de negócio e entidades centrais da aplicação.
"""

# Interfaces de domínio (definidas localmente para evitar dependências externas)
class TaskManagerInterface:
    """Interface para gerenciadores de tarefas"""
    pass

class TessManager:
    """Gerenciador TESS simplificado"""
    pass

class TaskManagerFactory:
    """Fábrica de gerenciadores de tarefas"""
    @staticmethod
    def create():
        return None

__all__ = [
    "TaskManagerInterface",
    "TessManager",
    "TaskManagerFactory"
] 