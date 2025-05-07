FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

# Asegurarnos de que la carpeta public exista
RUN mkdir -p public

RUN npm run build

# Usar nginx para servir la aplicación
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
COPY --from=0 /app/build/index.html /usr/share/nginx/html/index.html

# Configuración para SPA routing
RUN echo "server { \
    listen 3000; \
    root /usr/share/nginx/html; \
    location / { \
        try_files \$uri \$uri/ /index.html; \
    } \
}" > /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"] 