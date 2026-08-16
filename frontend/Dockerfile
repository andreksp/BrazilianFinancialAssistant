# Multi-stage build — Brazilian Financial Assistant Frontend
# Stage 1: build Angular app
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --prefer-offline

COPY . .
RUN npm run build -- --configuration production

# Stage 2: serve with nginx
FROM nginx:alpine

COPY --from=builder /app/dist/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD wget -qO- http://localhost/health || exit 1

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
