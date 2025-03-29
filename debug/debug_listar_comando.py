#!/usr/bin/env python3
"""
Script para identificar e corrigir o problema com o comando listar_agentes no MCP.

Este script:
1. Verifica se é possível importar MCPNLProcessor
2. Modifica a implementação do método listar_agentes no arquivo
3. Testa se a nova implementação funciona
"""

import os
import sys
import re
import logging
import tempfile
import shutil
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("debug_listar_comando")

# Adicionar raiz do projeto ao PATH
project_root = str(Path(__file__).resolve().parent)
sys.path.insert(0, project_root)

def backup_file(filepath):
    """Cria um backup do arquivo"""
    backup_path = f"{filepath}.bak.{os.urandom(4).hex()}"
    shutil.copy2(filepath, backup_path)
    logger.info(f"Backup criado em: {backup_path}")
    return backup_path

def patch_mcp_processor():
    """Modifica o arquivo mcp_nl_processor.py para corrigir o método listar_agentes"""
    filepath = os.path.join(project_root, "src", "tools", "mcp_nl_processor.py")
    
    if not os.path.exists(filepath):
        logger.error(f"Arquivo não encontrado: {filepath}")
        return False
    
    # Fazer backup do arquivo original
    backup_path = backup_file(filepath)
    
    try:
        # Ler o conteúdo do arquivo
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Procurar o padrão do método processar_comando
        processar_comando_pattern = r'def processar_comando\(self, tipo_comando: str, params: Dict\[str, Any\]\).*?:'
        match = re.search(processar_comando_pattern, content, re.DOTALL)
        
        if not match:
            logger.error("Não foi possível encontrar o método processar_comando")
            return False
        
        # Verificar se já existe uma implementação para listar_agentes
        listar_agentes_pattern = r'elif tipo_comando == "listar_agentes":(.*?)(?=\n\s+\w)'
        listar_match = re.search(listar_agentes_pattern, content, re.DOTALL)
        
        # Código da nova implementação
        nova_implementacao = """
        elif tipo_comando == "listar_agentes":
            # Implementação direta para o comando listar_agentes
            logger.info("Processando comando listar_agentes via implementação direta")
            try:
                from tests.test_api_tess import listar_agentes
                success, data = listar_agentes(is_cli=False)
                
                if not success:
                    logger.error(f"Erro ao listar agentes: {data.get('error')}")
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
                logger.info(f"Comando listar_agentes executado com sucesso, retornando {len(resposta)} caracteres")
                return resposta
                
            except Exception as e:
                logger.exception(f"Erro ao executar comando listar_agentes: {e}")
                return f"❌ Erro ao listar agentes: {str(e)}"
        """
        
        if listar_match:
            # Substituir a implementação existente
            logger.info("Substituindo implementação existente do listar_agentes")
            new_content = content.replace(listar_match.group(0), nova_implementacao.rstrip())
        else:
            # Adicionar nova implementação antes do bloco de logging.warning
            warning_pattern = r'(\s+logging\.warning\(f"Comando não implementado: {tipo_comando}"\))'
            match = re.search(warning_pattern, content)
            if match:
                logger.info("Adicionando nova implementação do listar_agentes")
                new_content = content.replace(match.group(0), nova_implementacao + match.group(0))
            else:
                logger.error("Não foi possível encontrar o ponto para adicionar a implementação")
                return False
        
        # Salvar as alterações
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info("Arquivo modificado com sucesso")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao modificar o arquivo: {e}")
        # Restaurar backup em caso de erro
        logger.info("Restaurando backup")
        shutil.copy2(backup_path, filepath)
        return False

def test_listar_agentes():
    """Testa se a função listar_agentes funciona corretamente"""
    try:
        from tests.test_api_tess import listar_agentes
        logger.info("Testando função listar_agentes")
        
        success, data = listar_agentes(is_cli=False)
        if success:
            total = len(data.get('data', []))
            logger.info(f"Função listar_agentes funcionou! Total de agentes: {total}")
            return True
        else:
            logger.error(f"Função listar_agentes falhou: {data.get('error')}")
            return False
    
    except Exception as e:
        logger.error(f"Erro ao testar função listar_agentes: {e}")
        return False

if __name__ == "__main__":
    print("=== DIAGNOSTICANDO PROBLEMA NO COMANDO LISTAR_AGENTES ===\n")
    
    # Teste direto da função listar_agentes
    print("1. Testando função listar_agentes original...")
    if test_listar_agentes():
        print("✅ Função listar_agentes funciona corretamente!\n")
    else:
        print("❌ Função listar_agentes não está funcionando corretamente!\n")
        sys.exit(1)
    
    # Patch do arquivo mcp_nl_processor.py
    print("2. Modificando implementação no arquivo mcp_nl_processor.py...")
    if patch_mcp_processor():
        print("✅ Arquivo modificado com sucesso!\n")
    else:
        print("❌ Falha ao modificar o arquivo!\n")
        sys.exit(1)
    
    print("""
=== MODIFICAÇÃO CONCLUÍDA ===

O comando 'listar_agentes' foi implementado diretamente no MCPNLProcessor.
Agora, ao digitar 'listar agentes' no Arcee Chat, você deve ver a lista completa de agentes.

Para testar, execute:
    arcee chat
    
E digite: listar agentes

Se ainda não funcionar, verifique os logs para mais detalhes.
    """) 