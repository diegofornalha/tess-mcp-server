# Imagem base
FROM node:18-alpine

# Variáveis de ambiente
ENV NODE_ENV=production

# Diretório de trabalho
WORKDIR /app

# Instalar pacotes do sistema necessários
RUN apk add --no-cache curl

# Copiar arquivos de dependências e instalar
COPY package*.json ./
RUN npm ci --only=production

# Copiar código fonte
COPY . .

# Expor porta
EXPOSE 3001

# Verificação de saúde
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3001/health || exit 1

# Comando para iniciar o servidor
CMD ["node", "src/index.js"]