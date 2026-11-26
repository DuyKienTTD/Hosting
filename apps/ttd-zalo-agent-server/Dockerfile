FROM node:24-bookworm-slim AS build
WORKDIR /workspace/ttd-zalo-agent-server
COPY apps/ttd-zalo-agent-server/package*.json ./
RUN npm ci --no-audit --no-fund
COPY apps/ttd-zalo-agent-server/src ./src
COPY apps/ttd-zalo-agent-server/tsconfig.json ./
COPY apps/ttd-zalo-assistant/src /workspace/ttd-zalo-assistant/src
RUN npm run build && rm dist/ttd-zalo-agent-server/src/local-store.js

FROM node:24-bookworm-slim
WORKDIR /app
COPY apps/ttd-zalo-agent-server/package*.json ./
RUN npm ci --omit=dev --no-audit --no-fund
ARG INSTALL_UI_BROWSER=0
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright
RUN if [ "$INSTALL_UI_BROWSER" = 1 ]; then npx playwright install --with-deps chromium && rm -rf /var/lib/apt/lists/*; fi
COPY --from=build /workspace/ttd-zalo-agent-server/dist ./dist
USER node
CMD ["node","dist/ttd-zalo-agent-server/src/main.js"]
