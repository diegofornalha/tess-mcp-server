#!/bin/bash
# Script para atualizar o pacote npm @diegofornalha/crew-ai-tess-pareto

set -e  # Interrompe o script se algum comando falhar

echo "==== Atualizando pacote npm @diegofornalha/crew-ai-tess-pareto ===="

# Verifica se o npm está instalado
if ! command -v npm &> /dev/null; then
    echo "Erro: npm não está instalado. Por favor, instale o npm primeiro."
    exit 1
fi

# Verifica se está logado no npm
if ! npm whoami &> /dev/null; then
    echo "Você não está autenticado no npm. Por favor, execute 'npm login' primeiro."
    exit 1
fi

echo "Usuário npm atual: $(npm whoami)"

# Opções de atualização de versão
echo "Escolha o tipo de atualização de versão:"
echo "1. Patch (1.0.0 -> 1.0.1) - correções de bugs"
echo "2. Minor (1.0.0 -> 1.1.0) - novos recursos compatíveis"
echo "3. Major (1.0.0 -> 2.0.0) - mudanças incompatíveis"
echo "4. Versão específica (você digitará a versão)"
read -p "Opção (1-4): " version_option

case $version_option in
    1)
        npm version patch
        ;;
    2)
        npm version minor
        ;;
    3)
        npm version major
        ;;
    4)
        read -p "Digite a nova versão (ex: 1.2.3): " specific_version
        npm version $specific_version --no-git-tag-version
        ;;
    *)
        echo "Opção inválida. Saindo."
        exit 1
        ;;
esac

# Verifica dependência cíclica
if grep -q "\"@diegofornalha/crew-ai-tess-pareto\":" package.json; then
    echo "AVISO: Detectada dependência cíclica no package.json!"
    read -p "Deseja remover a dependência cíclica? (s/n): " remove_dep
    if [ "$remove_dep" = "s" ]; then
        # Usa o comando npm para remover a dependência cíclica
        npm uninstall @diegofornalha/crew-ai-tess-pareto
        echo "Dependência cíclica removida."
    fi
fi

# Executa testes se existirem
if grep -q "\"test\":" package.json; then
    read -p "Deseja executar os testes antes de publicar? (s/n): " run_tests
    if [ "$run_tests" = "s" ]; then
        echo "Executando testes..."
        npm test || { echo "Testes falharam. Deseja continuar mesmo assim? (s/n): "; read cont; [ "$cont" != "s" ] && exit 1; }
    fi
fi

# Empacota o código
echo "Criando pacote de teste..."
npm pack

# Pergunta se o usuário quer verificar o conteúdo do pacote
read -p "Deseja verificar o conteúdo do pacote gerado? (s/n): " check_package
if [ "$check_package" = "s" ]; then
    # Lista o conteúdo do arquivo tgz mais recente
    newest_tarball=$(ls -t *tess-pareto-*.tgz | head -1)
    echo "Conteúdo do pacote $newest_tarball:"
    tar -tf $newest_tarball | less
    read -p "Pressione Enter para continuar..."
fi

# Confirmação final
read -p "Tudo pronto! Deseja publicar o pacote no npm? (s/n): " publish_confirm
if [ "$publish_confirm" = "s" ]; then
    echo "Publicando pacote no npm..."
    npm publish --access public
    
    # Verifica se a publicação foi bem-sucedida
    if [ $? -eq 0 ]; then
        echo "==== Pacote publicado com sucesso! ===="
        npm view @diegofornalha/crew-ai-tess-pareto version
        echo "Para instalar, execute: npm install @diegofornalha/crew-ai-tess-pareto"
    else
        echo "Erro ao publicar o pacote. Verifique o log acima."
    fi
else
    echo "Publicação cancelada pelo usuário."
fi 