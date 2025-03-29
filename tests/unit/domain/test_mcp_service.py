#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Testes unitários para o serviço MCP.

Este módulo contém testes para o serviço MCPService.
"""

import unittest
from unittest.mock import Mock, patch

from domain.interfaces.mcp_client import MCPClientInterface
from domain.services.mcp_service import MCPService
from domain.exceptions import ToolNotFoundError, ToolExecutionError


class TestMCPService(unittest.TestCase):
    """Testes para o serviço MCPService."""
    
    def setUp(self):
        """Configura o ambiente para os testes."""
        # Criar mock para o cliente MCP
        self.mock_client = Mock(spec=MCPClientInterface)
        
        # Criar o serviço usando o mock
        self.service = MCPService(mcp_client=self.mock_client)
        
        # Configurar mock para retornar ferramentas de exemplo
        self.mock_tools = [
            {
                "id": "tool1",
                "name": "Ferramenta 1",
                "description": "Descrição da ferramenta 1",
                "category": "categoria1"
            },
            {
                "id": "tool2",
                "name": "Ferramenta 2",
                "description": "Descrição da ferramenta 2",
                "category": "categoria2"
            }
        ]
        self.mock_client.list_tools.return_value = self.mock_tools
    
    def test_list_tools(self):
        """Testa se o serviço lista ferramentas corretamente."""
        # Chamar o método do serviço
        tools = self.service.list_tools()
        
        # Verificar se o método do cliente foi chamado
        self.mock_client.list_tools.assert_called_once()
        
        # Verificar se o resultado é o esperado
        self.assertEqual(tools, self.mock_tools)
    
    def test_get_tool_details_found(self):
        """Testa se o serviço obtém detalhes de uma ferramenta existente."""
        # Configurar mock para retornar uma ferramenta específica
        expected_tool = self.mock_tools[0]
        self.mock_client.get_tool.return_value = expected_tool
        
        # Chamar o método do serviço
        tool = self.service.get_tool_details("tool1")
        
        # Verificar se o método do cliente foi chamado corretamente
        self.mock_client.get_tool.assert_called_once_with("tool1")
        
        # Verificar se o resultado é o esperado
        self.assertEqual(tool, expected_tool)
    
    def test_get_tool_details_not_found(self):
        """Testa se o serviço lança exceção para ferramenta não existente."""
        # Configurar mock para retornar None (ferramenta não encontrada)
        self.mock_client.get_tool.return_value = None
        
        # Verificar se a exceção esperada é lançada
        with self.assertRaises(ToolNotFoundError):
            self.service.get_tool_details("tool_inexistente")
        
        # Verificar se o método do cliente foi chamado corretamente
        self.mock_client.get_tool.assert_called_once_with("tool_inexistente")
    
    def test_execute_tool_success(self):
        """Testa se o serviço executa uma ferramenta com sucesso."""
        # Configurar mocks
        tool_id = "tool1"
        expected_result = {"output": "resultado da execução"}
        
        self.mock_client.get_tool.return_value = self.mock_tools[0]
        self.mock_client.execute_tool.return_value = expected_result
        
        # Parâmetros para execução
        params = {"param1": "valor1"}
        
        # Chamar o método do serviço
        result = self.service.execute_tool(tool_id, params)
        
        # Verificar se os métodos do cliente foram chamados corretamente
        self.mock_client.get_tool.assert_called_once_with(tool_id)
        self.mock_client.execute_tool.assert_called_once_with(tool_id, params)
        
        # Verificar se o resultado é o esperado
        self.assertEqual(result, expected_result)
    
    def test_execute_tool_not_found(self):
        """Testa se o serviço lança exceção ao executar ferramenta inexistente."""
        # Configurar mock para retornar None (ferramenta não encontrada)
        self.mock_client.get_tool.return_value = None
        
        # Verificar se a exceção esperada é lançada
        with self.assertRaises(ToolNotFoundError):
            self.service.execute_tool("tool_inexistente", {})
        
        # Verificar se apenas o método get_tool foi chamado (execute_tool não deve ser chamado)
        self.mock_client.get_tool.assert_called_once_with("tool_inexistente")
        self.mock_client.execute_tool.assert_not_called()
    
    def test_execute_tool_execution_error(self):
        """Testa se o serviço lança exceção quando há erro na execução."""
        # Configurar mocks
        tool_id = "tool1"
        
        self.mock_client.get_tool.return_value = self.mock_tools[0]
        self.mock_client.execute_tool.side_effect = Exception("Erro na execução")
        
        # Verificar se a exceção esperada é lançada
        with self.assertRaises(ToolExecutionError):
            self.service.execute_tool(tool_id, {})
        
        # Verificar se os métodos do cliente foram chamados corretamente
        self.mock_client.get_tool.assert_called_once_with(tool_id)
        self.mock_client.execute_tool.assert_called_once_with(tool_id, {})
    
    def test_get_tool_categories(self):
        """Testa se o serviço obtém as categorias de ferramentas corretamente."""
        # Categorias esperadas baseadas nas ferramentas mock
        expected_categories = ["categoria1", "categoria2"]
        
        # Chamar o método do serviço
        categories = self.service.get_tool_categories()
        
        # Verificar se o método do cliente foi chamado
        self.mock_client.list_tools.assert_called_once()
        
        # Verificar se o resultado é o esperado (categorias ordenadas)
        self.assertEqual(categories, expected_categories)
    
    def test_get_tools_by_category(self):
        """Testa se o serviço filtra ferramentas por categoria corretamente."""
        # Chamar o método do serviço
        tools = self.service.get_tools_by_category("categoria1")
        
        # Verificar se o método do cliente foi chamado
        self.mock_client.list_tools.assert_called_once()
        
        # Verificar se o resultado contém apenas ferramentas da categoria solicitada
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]["id"], "tool1")
        self.assertEqual(tools[0]["category"], "categoria1")
    
    def test_find_tool_by_name_exact_match(self):
        """Testa se o serviço encontra uma ferramenta pelo nome exato."""
        # Chamar o método do serviço
        tool = self.service.find_tool_by_name("Ferramenta 1")
        
        # Verificar se o método do cliente foi chamado
        self.mock_client.list_tools.assert_called_once()
        
        # Verificar se o resultado é a ferramenta correta
        self.assertIsNotNone(tool)
        self.assertEqual(tool["id"], "tool1")
    
    def test_find_tool_by_name_partial_match(self):
        """Testa se o serviço encontra uma ferramenta por correspondência parcial."""
        # Chamar o método do serviço
        tool = self.service.find_tool_by_name("ferramenta 2")  # Nome em minúsculas
        
        # Verificar se o método do cliente foi chamado
        self.mock_client.list_tools.assert_called_once()
        
        # Verificar se o resultado é a ferramenta correta
        self.assertIsNotNone(tool)
        self.assertEqual(tool["id"], "tool2")
    
    def test_find_tool_by_name_not_found(self):
        """Testa se o serviço retorna None quando uma ferramenta não é encontrada."""
        # Chamar o método do serviço
        tool = self.service.find_tool_by_name("Ferramenta Inexistente")
        
        # Verificar se o método do cliente foi chamado
        self.mock_client.list_tools.assert_called_once()
        
        # Verificar se o resultado é None
        self.assertIsNone(tool)


if __name__ == "__main__":
    unittest.main() 