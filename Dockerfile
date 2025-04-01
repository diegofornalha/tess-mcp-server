# Imagem base
FROM node:18-alpine

# Criar diretório da aplicação
WORKDIR /app

# Copiar arquivos de configuração
COPY package*.json ./
COPY smithery.yaml ./

# Instalar dependências
RUN npm ci --only=production

# Copiar código fonte
COPY src/ ./src/
COPY scripts/ ./scripts/

# Definir variáveis de ambiente
ENV NODE_ENV=production
ENV PORT=3001

# Tornar scripts executáveis
RUN chmod +x ./scripts/*.sh

# Expor porta
EXPOSE 3001

# Verificação de saúde
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3001/health || exit 1

# Iniciar aplicação
CMD ["node", "src/index.js"]