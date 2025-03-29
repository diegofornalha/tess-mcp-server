#!/usr/bin/env python3
import os
import sys
import logging
from pathlib import Path
import importlib.util

# Adicionar raiz do projeto ao PATH
project_root = str(Path(__file__).resolve().parent)
sys.path.insert(0, project_root)

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("debug_cli")

# Verificar ambiente
try:
    # Importar módulo diretamente sem depender das importações completas
    spec = importlib.util.spec_from_file_location(
        "mcp_nl_processor", 
        os.path.join(project_root, "src", "tools", "mcp_nl_processor.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Criar instância do processador
    MCPNLProcessor = module.MCPNLProcessor
    processor = MCPNLProcessor()
    logger.info("MCPNLProcessor inicializado com sucesso via importação direta")
    
    # Detectar e processar comandos
    comando = sys.argv[1] if len(sys.argv) > 1 else "listar agentes"
    logger.info(f"Executando detecção de comando para: {comando}")
    
    is_comando, tipo_comando, params = processor.detectar_comando(comando)
    logger.info(f"Resultado da detecção: is_comando={is_comando}, tipo_comando={tipo_comando}, params={params}")
    
    if is_comando:
        logger.info(f"Processando comando: {tipo_comando}")
        resposta = processor.processar_comando(tipo_comando, params)
        logger.info(f"Resposta (primeiros 100 caracteres): {resposta[:100] if resposta else None}")
        print("\n=== RESPOSTA DO COMANDO ===")
        print(resposta)
        print("==========================\n")
    else:
        print("Comando não detectado!")
        
    # Importar diretamente a função listar_agentes para comparação
    spec_test = importlib.util.spec_from_file_location(
        "test_api_tess", 
        os.path.join(project_root, "tests", "test_api_tess.py")
    )
    test_module = importlib.util.module_from_spec(spec_test)
    spec_test.loader.exec_module(test_module)
    
    print("\n=== TESTE DIRETO DA FUNÇÃO LISTAR_AGENTES ===")
    success, data = test_module.listar_agentes(is_cli=False)
    if success:
        print(f"Função direta funcionou! Total de agentes: {len(data.get('data', []))}")
    else:
        print(f"Função direta falhou: {data.get('error', 'Erro desconhecido')}")
    print("=============================================\n")
    
except Exception as e:
    logger.error(f"Erro ao executar debug_cli: {e}")
    import traceback
    traceback.print_exc() 