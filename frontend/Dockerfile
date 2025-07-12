# --- Build Stage ---
FROM node:18-alpine AS build
WORKDIR /app

# Install pnpm (faster than npm)
RUN npm install -g pnpm --registry=https://registry.npmmirror.com

# Configure pnpm for better performance
RUN pnpm config set registry https://registry.npmmirror.com

# Copy package files and install dependencies with cache mount
COPY package*.json ./
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    --mount=type=cache,target=/tmp/.pnpm-store \
    pnpm install --frozen-lockfile=false --silent

# Copy source code (excluding files in .dockerignore)
COPY . .

# Build the application
RUN pnpm run build

# --- Production Stage ---
FROM nginx:stable-alpine
WORKDIR /usr/share/nginx/html

# Remove default Nginx content
RUN rm -rf ./*

# Copy built files from the build stage
COPY --from=build /app/dist .

# Copy Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"] 