FROM nginx:alpine

# Copy login.html as index.html
COPY login.html /usr/share/nginx/html/index.html

# Copy all other static files
COPY . /usr/share/nginx/html/

# Configure nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 