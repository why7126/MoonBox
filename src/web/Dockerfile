ARG WEB_NODE_BASE_IMAGE=node:22-slim
ARG WEB_NGINX_BASE_IMAGE=nginx:1.27-alpine

FROM ${WEB_NODE_BASE_IMAGE} AS build
WORKDIR /app/src/web

COPY src/web/package.json src/web/pnpm-lock.yaml src/web/pnpm-workspace.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

COPY src/web/ ./
RUN pnpm build

FROM ${WEB_NGINX_BASE_IMAGE}
COPY --from=build /app/src/web/dist /usr/share/nginx/html

EXPOSE 80
