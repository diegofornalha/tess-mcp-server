#!/bin/bash

echo "=== Instalando Arcee CLI ==="

# Ativar ambiente virtual
source venv/bin/activate

# Instalar Arcee CLI
pip install arcee-cli

echo "✅ Arcee CLI instalado com sucesso!"
echo "Agora você pode usar o Arcee CLI diretamente ou através da aplicação Streamlit."
echo ""
echo "Para testar o Arcee CLI, execute:"
echo "arcee --version"
echo ""
echo "Para iniciar a aplicação Streamlit com suporte ao Arcee:"
echo "./setup_fix.sh" 