FROM node:20-alpine

WORKDIR /app

# Copiar dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar código
COPY . .

# Build
RUN npm run build

# Exponer puerto
EXPOSE 3010

# Iniciar
CMD ["npm", "start"]
