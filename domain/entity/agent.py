#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Entidade Agent (Agente) do domínio.

Esta entidade representa um agente no sistema, contendo suas propriedades
e regras de negócio associadas.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class Agent:
    """
    Entidade que representa um Agente no sistema.
    
    Um Agente é um assistente inteligente que pode executar tarefas específicas
    baseadas em suas capacidades e configurações.
    """
    
    id: str
    name: str
    description: str
    version: str
    type: str
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validações e inicializações após a criação da instância."""
        self._validate()
    
    def _validate(self) -> None:
        """
        Valida os campos da entidade.
        
        Raises:
            ValueError: Se campos obrigatórios estiverem inválidos.
        """
        if not self.id:
            raise ValueError("ID do agente não pode ser vazio")
            
        if not self.name:
            raise ValueError("Nome do agente não pode ser vazio")
            
        if not self.type:
            raise ValueError("Tipo do agente não pode ser vazio")
    
    def has_capability(self, capability: str) -> bool:
        """
        Verifica se o agente possui uma determinada capacidade.
        
        Args:
            capability: A capacidade a ser verificada.
            
        Returns:
            bool: True se o agente possuir a capacidade, False caso contrário.
        """
        return capability in self.capabilities
    
    def add_capability(self, capability: str) -> None:
        """
        Adiciona uma capacidade ao agente.
        
        Args:
            capability: A capacidade a ser adicionada.
        """
        if capability not in self.capabilities:
            self.capabilities.append(capability)
            self.updated_at = datetime.now()
    
    def remove_capability(self, capability: str) -> bool:
        """
        Remove uma capacidade do agente.
        
        Args:
            capability: A capacidade a ser removida.
            
        Returns:
            bool: True se a capacidade foi removida, False se não existia.
        """
        if capability in self.capabilities:
            self.capabilities.remove(capability)
            self.updated_at = datetime.now()
            return True
        return False
    
    def update_metadata(self, key: str, value: Any) -> None:
        """
        Atualiza um valor nos metadados do agente.
        
        Args:
            key: A chave do metadado.
            value: O valor a ser armazenado.
        """
        self.metadata[key] = value
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte a entidade para um dicionário.
        
        Returns:
            Dict[str, Any]: Representação da entidade como dicionário.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "type": self.type,
            "capabilities": self.capabilities.copy(),
            "metadata": self.metadata.copy(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """
        Cria uma instância de Agent a partir de um dicionário.
        
        Args:
            data: Dicionário com os dados do agente.
            
        Returns:
            Agent: Nova instância de Agent.
        """
        agent_data = data.copy()
        
        # Converter strings ISO para datetime
        if "created_at" in agent_data and isinstance(agent_data["created_at"], str):
            agent_data["created_at"] = datetime.fromisoformat(agent_data["created_at"])
            
        if "updated_at" in agent_data and isinstance(agent_data["updated_at"], str):
            agent_data["updated_at"] = datetime.fromisoformat(agent_data["updated_at"])
        
        return cls(**agent_data) 