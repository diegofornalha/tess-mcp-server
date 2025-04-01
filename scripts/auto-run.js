/**
 * Execução automática de comandos no modo YOLO
 * Este script permite executar comandos sem confirmação manual
 */

const { spawn } = require('child_process');
const readline = require('readline');

// Configurações
const AUTO_RESTART = true;  // Reiniciar automaticamente o servidor se cair
const LOG_COMMANDS = true;  // Registrar comandos executados em log
const COMMAND_DELAY = 500;  // Atraso entre comandos em ms

// Interface de linha de comando
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: 'YOLO> '
});

// Cores para console
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  red: '\x1b[31m'
};

// Histórico de comandos
const commandHistory = [];

/**
 * Executa um comando no terminal
 * @param {string} command Comando a ser executado
 * @returns {Promise} Promessa com resultado da execução
 */
function executeCommand(command) {
  return new Promise((resolve, reject) => {
    console.log(`${colors.green}Executando:${colors.reset} ${command}`);
    
    // Registrar no histórico
    if (LOG_COMMANDS) {
      commandHistory.push({
        timestamp: new Date(),
        command
      });
    }
    
    // Dividir o comando em programa e argumentos
    const parts = command.split(' ');
    const program = parts[0];
    const args = parts.slice(1);
    
    const process = spawn(program, args, {
      shell: true,
      stdio: 'inherit'
    });
    
    process.on('close', (code) => {
      if (code === 0) {
        console.log(`${colors.green}Comando executado com sucesso (código ${code})${colors.reset}\n`);
        resolve(code);
      } else {
        console.log(`${colors.red}Comando falhou com código ${code}${colors.reset}\n`);
        resolve(code);
      }
      rl.prompt();
    });
    
    process.on('error', (error) => {
      console.error(`${colors.red}Erro ao executar comando: ${error.message}${colors.reset}\n`);
      reject(error);
      rl.prompt();
    });
  });
}

/**
 * Inicia o servidor TESS-MCP
 */
async function startServer() {
  console.log(`${colors.cyan}Iniciando servidor TESS-MCP...${colors.reset}`);
  return executeCommand('node src/index.js');
}

// Iniciar o modo YOLO
console.log(`
${colors.yellow}╔════════════════════════════════════════════╗
║             MODO YOLO ATIVADO             ║
║   Comandos executados automaticamente!    ║
║         Use 'exit' para encerrar          ║
╚════════════════════════════════════════════╝${colors.reset}
`);

// Comandos disponíveis
console.log(`${colors.cyan}Comandos especiais:${colors.reset}`);
console.log(`  ${colors.green}start${colors.reset}    - Inicia o servidor TESS-MCP`);
console.log(`  ${colors.green}history${colors.reset}  - Mostra histórico de comandos`);
console.log(`  ${colors.green}exit${colors.reset}     - Sai do modo YOLO\n`);

// Processar comandos interativamente
rl.prompt();

rl.on('line', async (line) => {
  const command = line.trim();
  
  if (!command) {
    rl.prompt();
    return;
  }
  
  // Comandos especiais
  if (command === 'exit') {
    console.log(`${colors.yellow}Saindo do modo YOLO...${colors.reset}`);
    rl.close();
    process.exit(0);
  } else if (command === 'start') {
    await startServer();
  } else if (command === 'history') {
    console.log(`${colors.cyan}Histórico de comandos:${colors.reset}`);
    commandHistory.forEach((item, index) => {
      const timestamp = item.timestamp.toLocaleTimeString();
      console.log(`  ${index + 1}. [${timestamp}] ${item.command}`);
    });
    rl.prompt();
  } else {
    await executeCommand(command);
  }
});

rl.on('close', () => {
  console.log(`${colors.yellow}Modo YOLO encerrado.${colors.reset}`);
  process.exit(0);
});

// Iniciar servidor por padrão
if (process.argv.includes('--start-server')) {
  setTimeout(() => startServer(), 500);
}