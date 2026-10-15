# StudyUp AI: imagen única con el frontend compilado y el backend FastAPI.
#
# Construir:  docker build --build-arg VITE_CLERK_PUBLISHABLE_KEY=pk_test_... -t studyup:v0.5 .
# Ejecutar:   docker run -d --name studyup --restart unless-stopped -p 80:8000 --env-file studyup.env studyup:v0.5
#
# Los secretos (clave de OpenRouter) se pasan al EJECUTAR con --env-file, nunca aquí.
# La clave publicable de Clerk sí entra al construir: es pública y Vite la necesita
# para compilar el frontend.

# --- Etapa 1: compilar el frontend con Node --------------------------------
FROM node:22-alpine AS frontend
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY index.html vite.config.ts tsconfig.json tsconfig.node.json tailwind.config.js postcss.config.js ./
COPY public ./public
COPY src ./src

ARG VITE_CLERK_PUBLISHABLE_KEY
RUN test -n "$VITE_CLERK_PUBLISHABLE_KEY" || { echo "Falta --build-arg VITE_CLERK_PUBLISHABLE_KEY"; exit 1; }
RUN npm run build

# --- Etapa 2: imagen final con Python ---------------------------------------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FRONTEND_DIR=/app/dist

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt "uvicorn>=0.27.1"

COPY api ./api
COPY --from=frontend /app/dist ./dist

# El servicio no se ejecuta como root.
RUN useradd --create-home --uid 10001 studyup
USER studyup

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4)"

# 0.0.0.0 para aceptar conexiones desde fuera del contenedor.
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000"]
