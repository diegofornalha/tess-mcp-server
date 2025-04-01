/**
 * Script para preparar o pacote para publicação no Smithery
 * 
 * Este script configura o projeto para publicação no registro Smithery.
 * Ele verifica a configuração, gera arquivos necessários e valida o projeto.
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');
const { execSync } = require('child_process');

// Cores para console
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  red: '\x1b[31m'
};

/**
 * Log colorido
 */
const log = {
  info: (msg) => console.log(`${colors.blue}ℹ️ ${msg}${colors.reset}`),
  success: (msg) => console.log(`${colors.green}✅ ${msg}${colors.reset}`),
  warn: (msg) => console.log(`${colors.yellow}⚠️ ${msg}${colors.reset}`),
  error: (msg) => console.log(`${colors.red}❌ ${msg}${colors.reset}`)
};

/**
 * Verifica se um arquivo existe
 */
function fileExists(filePath) {
  try {
    return fs.statSync(filePath).isFile();
  } catch (err) {
    return false;
  }
}

/**
 * Função principal
 */
async function main() {
  log.info('Iniciando preparação para publicação no Smithery...');
  
  try {
    // Verificar arquivo smithery.yaml
    const smitheryPath = path.join(process.cwd(), 'smithery.yaml');
    if (!fileExists(smitheryPath)) {
      log.error('Arquivo smithery.yaml não encontrado.');
      process.exit(1);
    }
    
    // Ler configuração do Smithery
    const smitheryConfig = yaml.load(fs.readFileSync(smitheryPath, 'utf8'));
    log.success(`Configuração do Smithery carregada: ${smitheryConfig.name} v${smitheryConfig.version}`);
    
    // Verificar se package.json está sincronizado
    const packagePath = path.join(process.cwd(), 'package.json');
    if (fileExists(packagePath)) {
      const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
      
      if (packageJson.version !== smitheryConfig.version) {
        log.warn(`Versão no smithery.yaml (${smitheryConfig.version}) difere do package.json (${packageJson.version}).`);
        
        // Atualizar smithery.yaml com versão do package.json
        smitheryConfig.version = packageJson.version;
        fs.writeFileSync(smitheryPath, yaml.dump(smitheryConfig));
        log.success(`Versão no smithery.yaml atualizada para ${packageJson.version}`);
      } else {
        log.success(`Versões sincronizadas (${packageJson.version})`);
      }
    }
    
    // Verificar arquivo principal
    const mainFile = smitheryConfig.main || 'src/index.js';
    const mainFilePath = path.join(process.cwd(), mainFile);
    
    if (!fileExists(mainFilePath)) {
      log.error(`Arquivo principal '${mainFile}' não encontrado.`);
      process.exit(1);
    }
    
    log.success(`Arquivo principal '${mainFile}' encontrado.`);
    
    // Verificar dependências (opcionalmente)
    try {
      log.info('Verificando dependências...');
      execSync('npm ls --depth=0', { stdio: 'pipe' });
      log.success('Dependências verificadas.');
    } catch (error) {
      log.warn('Problemas com dependências detectados. Verifique com npm ls.');
    }
    
    // Preparar para publicação
    log.info('Preparando para publicação...');
    
    // Verificar se o login no Smithery CLI é necessário
    // (Isso é feito automaticamente pelo comando de publicação)
    
    // Conclusão
    log.success('Projeto pronto para publicação no Smithery!');
    log.info(`Para publicar, execute: npm run smithery:publish`);
    
  } catch (error) {
    log.error(`Erro durante a preparação: ${error.message}`);
    process.exit(1);
  }
}

// Executar script
main().catch(err => {
  log.error(`Erro fatal: ${err.message}`);
  process.exit(1);
});