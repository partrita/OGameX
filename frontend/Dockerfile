FROM nginx:alpine

# Copy modern frontend assets
COPY frontend /usr/share/nginx/html

# Custom nginx configuration for SPA & API Proxy
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
