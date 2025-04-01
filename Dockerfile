# Multi-stage build for smaller final image
FROM python:3.13-slim AS builder

WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./

# Install uv for dependency management
RUN pip install uv && \
    uv pip install --system -e .

# Second stage for the final image
FROM python:3.13-slim

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . /app

# Create non-root user
RUN useradd -m mcp && \
    chown -R mcp:mcp /app && \
    mkdir -p /home/mcp/.kube && \
    chown -R mcp:mcp /home/mcp

# Switch to non-root user
USER mcp

# Default config location
ENV CONFIG_PATH=/app/config/config.yaml
ENV TRANSPORT=both
ENV PORT=8000
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Expose port for SSE
EXPOSE 8000

# Run the server
ENTRYPOINT ["python", "-m", "mcp_k8s_server.main"]
CMD ["--transport", "${TRANSPORT}", "--port", "${PORT}", "--host", "${HOST}", "--config", "${CONFIG_PATH}"]
