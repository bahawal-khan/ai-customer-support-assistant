# Production frontend image (docs/deployment/DEPLOYMENT_SPEC.md: single
# Hostinger VPS, no Vercel). Build context is frontend/ itself:
#
#   docker build -t ai-customer-support-frontend \
#     --build-arg NEXT_PUBLIC_API_URL=/api/v1 ./frontend
#
# NEXT_PUBLIC_API_URL is inlined into the JS bundle at build time (Next.js
# behavior, unrelated to this deployment) -- it is not a secret, only the
# path the browser calls, and is proxied to the backend by the host Nginx
# config (deploy/nginx/ai-customer-support.conf), so the default is a
# same-origin relative path rather than an absolute backend URL.

FROM node:20-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:20-slim AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG NEXT_PUBLIC_API_URL=/api/v1
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
RUN npm run build

FROM node:20-slim AS runner
WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000 \
    HOSTNAME=0.0.0.0

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD node -e "require('http').get('http://127.0.0.1:3000/', r => process.exit(r.statusCode < 500 ? 0 : 1)).on('error', () => process.exit(1))"

CMD ["node", "server.js"]
