FROM node:24-bookworm-slim AS build
WORKDIR /workspace/ttd-zalo-agent-server
COPY apps/ttd-zalo-agent-server/package*.json ./
RUN npm ci --no-audit --no-fund
COPY apps/ttd-zalo-agent-server/src ./src
COPY apps/ttd-zalo-agent-server/tsconfig.json ./
COPY apps/ttd-zalo-assistant/src /workspace/ttd-zalo-assistant/src
RUN npm run build

FROM node:24-bookworm-slim
WORKDIR /app
COPY apps/ttd-zalo-agent-server/package.json ./
RUN mkdir /data /backups && chown node:node /data /backups
COPY --from=build /workspace/ttd-zalo-agent-server/dist ./dist
USER node
ENV DB_PATH=/data/runtime.sqlite BACKUP_DIR=/backups
CMD ["node","dist/ttd-zalo-agent-server/src/main.js"]
