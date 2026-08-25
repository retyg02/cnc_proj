# --- ЭТАП 1: СБОРКА ИСХОДНОГО КОДА ---
FROM node:20-alpine AS builder
WORKDIR /app

# Копируем файлы конфигурации зависимостей JavaScript
COPY package*.json ./
RUN npm install

# Копируем весь код фронтенда и собираем его в статические файлы
COPY . .
RUN npm run build

# --- ЭТАП 2: РАЗДАЧА СТАТИКИ ЧЕРЕЗ ВЕБ-СЕРВЕР ---
FROM nginx:stable-alpine

# Копируем скомпилированные файлы из первого этапа (папка dist) в рабочую папку NGINX
COPY --from=builder /app/dist /usr/share/nginx/html

# Открываем стандартный веб-порт 80
EXPOSE 80

# Запускаем NGINX на постоянную работу в фоне
CMD ["nginx", "-g", "daemon off;"]
