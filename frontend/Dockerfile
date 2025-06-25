# ---------- build stage ----------
FROM node:22-bullseye AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build         # → dist/

# ---------- run stage ----------
FROM nginx:1.27-alpine
# Copy compiled assets
COPY --from=builder /app/dist /usr/share/nginx/html
# Copy custom nginx conf (added in next step)
COPY nginx.conf /etc/nginx/conf.d/default.conf
