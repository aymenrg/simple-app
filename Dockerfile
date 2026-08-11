# Step 1: Use an official ultra-lightweight web server image
FROM nginx:alpine

# Step 2: Copy your HTML file into Nginx's default public web directory
COPY index.html /usr/share/nginx/html/index.html

# Step 3: Inform Docker that the container listens on port 80
EXPOSE 80
