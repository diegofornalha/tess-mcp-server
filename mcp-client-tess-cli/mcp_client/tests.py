#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Testes unitários para o cliente MCP unificado
"""

import os
import sys
import unittest
from unittest import mock
from pathlib import Path

# Adicionar diretório raiz ao sys.path
project_root = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(0, project_root)

from infrastructure.mcp_client import MCPClientUnificado

class TestMCPClientUnificado(unittest.TestCase):
    """Testes para o cliente MCP unificado"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        # Mock das variáveis de ambiente
        self.env_patcher = mock.patch.dict(os.environ, {
            'MCP_SERVER_URL': 'http://localhost:8000',
            'VEYRAX_API_KEY': 'chave_teste_123',
            'MCPRUN_SERVER_URL': 'http://localhost:8001'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Limpeza após cada teste"""
        self.env_patcher.stop()
    
    def test_init_generic(self):
        """Testa inicialização do cliente genérico"""
        cliente = MCPClientUnificado(service_type="generic")
        self.assertEqual(cliente.service_type, "generic")
        self.assertEqual(cliente.base_url, "http://localhost:8000")
        self.assertIsNone(cliente.api_key)
    
    def test_init_veyrax(self):
        """Testa inicialização do cliente Veyrax"""
        cliente = MCPClientUnificado(service_type="veyrax")
        self.assertEqual(cliente.service_type, "veyrax")
        self.assertEqual(cliente.api_key, "chave_teste_123")
    
    def test_init_mcp_run(self):
        """Testa inicialização do cliente MCP.run"""
        cliente = MCPClientUnificado(service_type="mcp_run")
        self.assertEqual(cliente.service_type, "mcp_run")
        self.assertEqual(cliente.base_url, "http://localhost:8001")
    
    def test_init_invalid_service(self):
        """Testa inicialização com serviço inválido"""
        with self.assertRaises(ValueError):
            MCPClientUnificado(service_type="serviço_inexistente")
    
    @mock.patch('infrastructure.mcp_client.unified_client.requests.get')
    def test_get_tools_generic(self, mock_get):
        """Testa obter ferramentas do cliente genérico"""
        # Configura mock
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': [{'name': 'echo', 'description': 'Ferramenta de eco'}]
        }
        mock_get.return_value = mock_response
        
        # Testa
        cliente = MCPClientUnificado(service_type="generic")
        success, tools = cliente.get_tools()
        
        # Verifica
        self.assertTrue(success)
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]['name'], 'echo')
        mock_get.assert_called_once_with(
            'http://localhost:8000/tools',
            headers={'Content-Type': 'application/json'}
        )
    
    @mock.patch('infrastructure.mcp_client.unified_client.requests.post')
    def test_run_tool_generic(self, mock_post):
        """Testa executar ferramenta do cliente genérico"""
        # Configura mock
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': 'Resultado do teste'
        }
        mock_post.return_value = mock_response
        
        # Testa
        cliente = MCPClientUnificado(service_type="generic")
        success, result = cliente.run_tool('echo', 'say', {'message': 'Teste'})
        
        # Verifica
        self.assertTrue(success)
        self.assertEqual(result, 'Resultado do teste')
        mock_post.assert_called_once()
    
    @mock.patch('infrastructure.mcp_client.unified_client.requests.post')
    def test_save_memory_veyrax(self, mock_post):
        """Testa salvar memória no cliente Veyrax"""
        # Configura mock
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': {'id': '123', 'content': 'Teste'}
        }
        mock_post.return_value = mock_response
        
        # Testa
        cliente = MCPClientUnificado(service_type="veyrax")
        success, result = cliente.save_memory('Teste', 'teste')
        
        # Verifica
        self.assertTrue(success)
        self.assertEqual(result['id'], '123')
        mock_post.assert_called_once()
    
    @mock.patch('infrastructure.mcp_client.unified_client.requests.post')
    def test_start_session_mcp_run(self, mock_post):
        """Testa iniciar sessão no cliente MCP.run"""
        # Configura mock
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'success': True,
            'data': {'session_id': 'abc123'}
        }
        mock_post.return_value = mock_response
        
        # Testa
        cliente = MCPClientUnificado(service_type="mcp_run")
        success, session = cliente.start_session()
        
        # Verifica
        self.assertTrue(success)
        self.assertEqual(session['session_id'], 'abc123')
        mock_post.assert_called_once()

if __name__ == '__main__':
    unittest.main() 