# Intangible Valuation MCP server — stdio transport.
#
# Used by Glama (and the Official MCP Registry) for reproducible sandboxed
# introspection: build this image, run it, and the server answers tools/list over
# stdio. No environment variables or network access required. The package version
# is pinned in pyproject.toml; bump it alongside each release.

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install the library + MCP extra (fastmcp). The root wheel ships both the engine
# (src/) and the stdio server package (mcp_server/), so both must be present when
# the build backend runs — copy them before installing.
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY mcp_server ./mcp_server

RUN pip install ".[mcp]"

# stdio MCP server — stdout carries the protocol; keep it clean.
ENTRYPOINT ["intangible-valuation-mcp"]
