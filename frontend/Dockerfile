# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# Default Nginx config usually works for simple static/SPA if we add try_files for React Router
# But here we mostly have a single page or hash router?
# Let's add a simple custom Nginx config snippet to handle SPA routing if needed
# For now, default is safer unless we know we need SPA routing support (History API).
# Given it's a dashboard, it likely needs try_files $uri $uri/ /index.html;
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
