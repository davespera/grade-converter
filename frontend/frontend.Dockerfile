# Stage 1: Install all dependencies (including devDependencies)
FROM node:22-alpine AS deps
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --legacy-peer-deps
# Try to remove flag in the future

# Stage 2: Development (Target for local live-reloading)
FROM deps AS development
COPY frontend/ .
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]

# Stage 3: Build the application
FROM deps AS builder
COPY frontend/ .
RUN npm run build
RUN npm prune --production

# Stage 4: Final Production image
FROM node:22-alpine AS production
WORKDIR /app/frontend
COPY --from=builder /app/frontend/build build/
COPY --from=builder /app/frontend/node_modules node_modules/
COPY --from=builder /app/frontend/package.json .
EXPOSE 3000
ENV NODE_ENV=production
CMD [ "node", "build" ]