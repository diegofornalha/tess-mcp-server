#!/usr/bin/env python3
"""
Script para verificar comandos do TESS diretamente no ambiente do Cursor Agent.
Executa os comandos e mostra os resultados sem abrir interfaces externas.
"""

import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("cursor_tess_checker")

# Adicionar raiz do projeto ao PATH
project_root = str(Path(__file__).resolve().parent)
sys.path.insert(0, project_root)

def verificar_comando(comando):
    """Verifica a execução de um comando específico"""
    print(f"\n=== VERIFICANDO COMANDO: {comando} ===\n")
    
    try:
        # Importar a função diretamente
        if "chat" in comando.lower():
            from tests.test_api_tess import listar_agentes
            success, data = listar_agentes(is_cli=False, filter_type="chat")
            tipo = "chat"
        elif "text" in comando.lower() or "texto" in comando.lower():
            from tests.test_api_tess import listar_agentes
            success, data = listar_agentes(is_cli=False, filter_type="text")
            tipo = "text"
        else:
            from tests.test_api_tess import listar_agentes
            success, data = listar_agentes(is_cli=False)
            tipo = "todos"
        
        if success:
            total = len(data.get('data', []))
            print(f"✅ Sucesso! Encontrados {total} agentes do tipo: {tipo}")
            
            # Exibir os primeiros 10 resultados
            for i, agente in enumerate(data.get('data', [])[:10], 1):
                tipo_agente = agente.get('type', 'desconhecido')
                titulo = agente.get('title', 'Sem título')
                slug = agente.get('slug', 'N/A')
                print(f"{i}. {titulo} [{tipo_agente}] - Slug: {slug}")
            
            if total > 10:
                print(f"... e mais {total - 10} agentes")
                
            # Verificar implementação no MCPNLProcessor
            print("\n--- DIAGNÓSTICO DO PROBLEMA ---")
            try:
                from src.tools.mcp_nl_processor import MCPNLProcessor
                processor = MCPNLProcessor()
                is_comando, tipo_comando, params = processor.detectar_comando(comando)
                
                if is_comando:
                    print(f"✅ Comando detectado corretamente como: {tipo_comando}")
                    try:
                        resposta = processor.processar_comando(tipo_comando, params)
                        if "não implementado" in resposta:
                            print("❌ O processador retorna 'Comando não implementado'")
                            print("   Isso indica que o método está definido mas não implementado corretamente")
                            corrigir = input("Deseja corrigir a implementação? (s/n): ")
                            if corrigir.lower() == 's':
                                corrigir_implementacao()
                        else:
                            print("✅ O processador retorna uma resposta válida")
                    except Exception as e:
                        print(f"❌ Erro ao processar comando: {e}")
                else:
                    print(f"❌ O comando '{comando}' não foi detectado pelo processador")
            except Exception as e:
                print(f"❌ Erro ao verificar processador: {e}")
            
            return True
        else:
            print(f"❌ Falha ao listar agentes: {data.get('error', 'Erro desconhecido')}")
            return False
    
    except Exception as e:
        print(f"❌ Erro ao verificar comando: {e}")
        return False

def corrigir_implementacao():
    """Corrige a implementação do comando listar_agentes no MCP"""
    try:
        # Localizar o arquivo
        filepath = os.path.join(project_root, "src", "tools", "mcp_nl_processor.py")
        
        # Ler o conteúdo do arquivo
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se já existe uma implementação
        listar_agentes_pattern = r'elif tipo_comando == "listar_agentes":(.*?)(?=\n\s+\w)'
        import re
        listar_match = re.search(listar_agentes_pattern, content, re.DOTALL)
        
        # Código da nova implementação
        nova_implementacao = """
        elif tipo_comando == "listar_agentes":
            # Implementação direta para o comando listar_agentes
            try:
                from tests.test_api_tess import listar_agentes
                success, data = listar_agentes(is_cli=False)
                
                if not success:
                    return f"❌ Erro ao listar agentes: {data.get('error', 'Erro desconhecido')}"
                
                # Formatar a resposta para exibição
                total_agentes = len(data.get('data', []))
                resposta = f"📋 Lista de agentes disponíveis (Total: {total_agentes}):\\n\\n"
                
                for i, agente in enumerate(data.get('data', []), 1):
                    # Obter o tipo do agente (chat, text, etc)
                    tipo_agente = agente.get('type', 'desconhecido')
                    tipo_icone = "💬" if tipo_agente == "chat" else "📝" if tipo_agente == "text" else "🔄"
                    
                    resposta += f"{i}. {agente.get('title', 'Sem título')} {tipo_icone}\\n"
                    resposta += f"   ID: {agente.get('id', 'N/A')}\\n"
                    resposta += f"   Slug: {agente.get('slug', 'N/A')}\\n"
                    resposta += f"   Tipo: {tipo_agente.capitalize()}\\n"
                    resposta += f"   Descrição: {agente.get('description', 'Sem descrição')}\\n\\n"
                
                resposta += "Para executar um agente, use: executar agente <slug> \\"sua mensagem aqui\\""
                return resposta
                
            except Exception as e:
                return f"❌ Erro ao listar agentes: {str(e)}"
        """
        
        # Backup do arquivo original
        backup_path = f"{filepath}.bak.{os.urandom(4).hex()}"
        import shutil
        shutil.copy2(filepath, backup_path)
        print(f"Backup criado em: {backup_path}")
        
        # Modificar o arquivo
        if listar_match:
            # Substituir a implementação existente
            new_content = content.replace(listar_match.group(0), nova_implementacao.rstrip())
        else:
            # Adicionar nova implementação antes do bloco de logging.warning
            warning_pattern = r'(\s+logging\.warning\(f"Comando não implementado: {tipo_comando}"\))'
            match = re.search(warning_pattern, content)
            if match:
                new_content = content.replace(match.group(0), nova_implementacao + match.group(0))
            else:
                print("❌ Não foi possível encontrar o ponto para adicionar a implementação")
                return False
        
        # Salvar as alterações
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ Implementação corrigida com sucesso!")
        return True
    
    except Exception as e:
        print(f"❌ Erro ao corrigir implementação: {e}")
        return False

if __name__ == "__main__":
    print("=== VERIFICADOR DE COMANDOS TESS PARA CURSOR AGENT ===")
    print("Este script verifica e diagnostica problemas com comandos TESS")
    
    # Verificar o ambiente
    print("\n--- VERIFICANDO AMBIENTE ---")
    try:
        from tests.test_api_tess import listar_agentes
        print("✅ Módulo test_api_tess disponível")
    except ImportError:
        print("❌ Módulo test_api_tess não disponível")
        sys.exit(1)
        
    try:
        from src.tools.mcp_nl_processor import MCPNLProcessor
        print("✅ Módulo MCPNLProcessor disponível")
    except ImportError:
        print("❌ Módulo MCPNLProcessor não disponível")
    
    # Executar verificações
    comandos = [
        "listar agentes",
        "listar agentes tipo chat",
        "listar agentes tipo texto"
    ]
    
    for comando in comandos:
        verificar_comando(comando)
    
    print("\n=== VERIFICAÇÃO CONCLUÍDA ===")
    print("A verificação de comandos foi concluída. Se quiser corrigir a implementação manualmente, execute:")
    print("   python cursor_verificar_comandos.py corrigir")
    
    # Verificar se há argumento para corrigir
    if len(sys.argv) > 1 and sys.argv[1] == "corrigir":
        print("\n--- CORRIGINDO IMPLEMENTAÇÃO ---")
        corrigir_implementacao() 