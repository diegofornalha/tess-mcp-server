#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Serviço de domínio para operações com Agentes.

Este serviço implementa a lógica de negócio relacionada a agentes,
operando sobre a entidade Agent e fornecendo funcionalidades
que não pertencem naturalmente à entidade.
"""

from typing import List, Dict, Any, Optional
from domain.entity.agent import Agent


class AgentService:
    """
    Serviço que implementa operações de negócio relacionadas a agentes.
    """
    
    def filter_agents_by_capability(self, agents: List[Agent], capability: str) -> List[Agent]:
        """
        Filtra agentes que possuem uma determinada capacidade.
        
        Args:
            agents: Lista de agentes a serem filtrados.
            capability: Capacidade a ser verificada.
            
        Returns:
            List[Agent]: Lista filtrada de agentes com a capacidade especificada.
        """
        return [agent for agent in agents if agent.has_capability(capability)]
    
    def filter_agents_by_type(self, agents: List[Agent], agent_type: str) -> List[Agent]:
        """
        Filtra agentes por tipo.
        
        Args:
            agents: Lista de agentes a serem filtrados.
            agent_type: Tipo de agente a ser verificado.
            
        Returns:
            List[Agent]: Lista filtrada de agentes do tipo especificado.
        """
        return [agent for agent in agents if agent.type == agent_type]
    
    def find_agent_by_id(self, agents: List[Agent], agent_id: str) -> Optional[Agent]:
        """
        Encontra um agente pelo ID.
        
        Args:
            agents: Lista de agentes a serem verificados.
            agent_id: ID do agente a ser encontrado.
            
        Returns:
            Optional[Agent]: O agente encontrado ou None se não existir.
        """
        for agent in agents:
            if agent.id == agent_id:
                return agent
        return None
    
    def find_compatible_agents(self, agents: List[Agent], required_capabilities: List[str]) -> List[Agent]:
        """
        Encontra agentes que possuem todas as capacidades requeridas.
        
        Args:
            agents: Lista de agentes a serem verificados.
            required_capabilities: Lista de capacidades requeridas.
            
        Returns:
            List[Agent]: Lista de agentes compatíveis.
        """
        compatible_agents = []
        
        for agent in agents:
            if all(agent.has_capability(cap) for cap in required_capabilities):
                compatible_agents.append(agent)
                
        return compatible_agents
    
    def get_available_capabilities(self, agents: List[Agent]) -> List[str]:
        """
        Obtém todas as capacidades disponíveis em um conjunto de agentes.
        
        Args:
            agents: Lista de agentes a serem analisados.
            
        Returns:
            List[str]: Lista de todas as capacidades únicas.
        """
        capabilities = set()
        
        for agent in agents:
            capabilities.update(agent.capabilities)
            
        return sorted(list(capabilities))
    
    def get_available_types(self, agents: List[Agent]) -> List[str]:
        """
        Obtém todos os tipos de agentes disponíveis.
        
        Args:
            agents: Lista de agentes a serem analisados.
            
        Returns:
            List[str]: Lista de todos os tipos únicos.
        """
        types = set()
        
        for agent in agents:
            types.add(agent.type)
            
        return sorted(list(types))
    
    def merge_agent_metadata(self, agents: List[Agent]) -> Dict[str, Any]:
        """
        Combina os metadados de múltiplos agentes em um único dicionário.
        
        Args:
            agents: Lista de agentes cujos metadados serão combinados.
            
        Returns:
            Dict[str, Any]: Metadados combinados.
        """
        merged_metadata = {}
        
        for agent in agents:
            # Para cada chave nos metadados do agente
            for key, value in agent.metadata.items():
                # Se a chave já existe nos metadados mesclados e ambos os valores são dicionários
                if key in merged_metadata and isinstance(merged_metadata[key], dict) and isinstance(value, dict):
                    # Mesclar dicionários recursivamente
                    merged_metadata[key].update(value)
                else:
                    # Caso contrário, simplesmente substituir o valor
                    merged_metadata[key] = value
                    
        return merged_metadata
    
    def create_agent_from_dict(self, data: Dict[str, Any]) -> Agent:
        """
        Cria um agente a partir de um dicionário, validando os dados.
        
        Args:
            data: Dicionário com os dados do agente.
            
        Returns:
            Agent: Novo agente criado.
            
        Raises:
            ValueError: Se os dados estiverem inválidos.
        """
        required_fields = ["id", "name", "description", "version", "type"]
        
        # Verificar campos obrigatórios
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Campo obrigatório ausente: {field}")
                
        # Criar agente com os dados fornecidos
        return Agent.from_dict(data) 