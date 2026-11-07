FROM node:24-slim
WORKDIR /app
RUN npm install --global pnpm@12.18.0
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml ./
COPY apps/web/package.json ./apps/web/package.json
COPY packages/api-client/package.json ./packages/api-client/package.json
RUN pnpm install --frozen-lockfile
COPY apps/web ./apps/web
COPY packages/api-client ./packages/api-client
ENV NEXT_TELEMETRY_DISABLED=1
ENV API_ORIGIN=http://api:8000
RUN pnpm build
USER node
EXPOSE 3000
CMD ["pnpm", "--filter", "@store/web", "start"]
