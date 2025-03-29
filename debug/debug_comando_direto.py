#!/usr/bin/env python3
"""
Script simplificado para testar o comando listar_agentes diretamente,
sem precisar abrir o Arcee Chat em outra janela.
"""

import os
import sys
import json
from pathlib import Path

# Adicionar raiz do projeto ao PATH
project_root = str(Path(__file__).resolve().parent)
sys.path.insert(0, project_root)

def separador():
    """Imprime uma linha separadora para melhorar a visualização"""
    print("\n" + "=" * 70 + "\n")

def main():
    """Função principal para testar o comando listar_agentes"""
    print("🔍 TESTE DO COMANDO LISTAR_AGENTES (DIRETO)\n")
    
    try:
        # Importar a função diretamente do módulo (sem dependências)
        from tests.test_api_tess import listar_agentes
        
        # Testar diferentes comandos
        comandos = [
            {"nome": "Listar todos os agentes", "tipo": None, "keyword": None},
            {"nome": "Listar agentes tipo chat", "tipo": "chat", "keyword": None},
            {"nome": "Listar agentes tipo text", "tipo": "text", "keyword": None},
            {"nome": "Listar agentes com IA", "tipo": None, "keyword": "IA"}
        ]
        
        for cmd in comandos:
            print(f"📋 TESTANDO: {cmd['nome']}")
            success, data = listar_agentes(is_cli=False, filter_type=cmd['tipo'], keyword=cmd['keyword'])
            
            if success:
                agentes = data.get('data', [])
                total = len(agentes)
                print(f"✅ SUCESSO! Encontrados {total} agentes\n")
                
                # Mostrar apenas 3 primeiros para não sobrecarregar
                for i, agente in enumerate(agentes[:3], 1):
                    tipo = agente.get('type', 'desconhecido')
                    icone = "💬" if tipo == "chat" else "📝" if tipo == "text" else "🔄"
                    print(f"{i}. {agente.get('title', 'Sem título')} {icone}")
                    print(f"   ID: {agente.get('id', 'N/A')}")
                    print(f"   Slug: {agente.get('slug', 'N/A')}")
                    print(f"   Tipo: {tipo}")
                    print()
                
                if total > 3:
                    print(f"... e mais {total - 3} agentes")
            else:
                print(f"❌ FALHA! {data.get('error', 'Erro desconhecido')}")
            
            separador()
            
        # Verificar implementação no MCPNLProcessor
        print("\n🔧 VERIFICANDO IMPLEMENTAÇÃO NO PROCESSADOR MCP\n")
        
        try:
            # Tentar importar MCPNLProcessor diretamente, sem dependências circulares
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "mcp_nl_processor", 
                os.path.join(project_root, "src", "tools", "mcp_nl_processor.py")
            )
            
            if spec:
                modulo = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(modulo)
                
                # Verificar se a classe MCPNLProcessor existe
                if hasattr(modulo, 'MCPNLProcessor'):
                    print("✅ Módulo MCPNLProcessor encontrado!")
                    
                    # Verificar implementação do comando listar_agentes
                    processor = modulo.MCPNLProcessor()
                    is_comando, tipo_comando, params = processor.detectar_comando("listar agentes")
                    
                    print(f"- Detecção de comando: {is_comando}")
                    print(f"- Tipo de comando: {tipo_comando}")
                    
                    if is_comando and tipo_comando == "listar_agentes":
                        print("✅ Comando 'listar_agentes' detectado corretamente!")
                        
                        # Testar execução do comando
                        print("\n🧪 EXECUTANDO COMANDO VIA PROCESSADOR...\n")
                        resposta = processor.processar_comando(tipo_comando, params)
                        
                        if "não implementado" in resposta:
                            print("❌ ERRO: Comando ainda retorna 'não implementado'!")
                            print("- Isso indica que a correção no arquivo mcp_nl_processor.py não foi aplicada corretamente.")
                        else:
                            print("✅ COMANDO EXECUTADO COM SUCESSO!")
                            print("- Primeiras 100 caracteres da resposta:")
                            print(resposta[:100] + "...")
                    else:
                        print("❌ Falha na detecção do comando 'listar_agentes'")
                else:
                    print("❌ Classe MCPNLProcessor não encontrada no módulo")
            else:
                print("❌ Não foi possível localizar o módulo mcp_nl_processor.py")
                
        except Exception as e:
            print(f"❌ Erro ao verificar implementação: {str(e)}")
            
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 