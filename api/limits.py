"""What the two HTTP handlers accept.

One implementation, because both `api/index.py` and `api/mcp.py` read a declared `Content-Length` and
both were wrong in the same way: the cap added in #67 bounded only the positive side, so
`Content-Length: -1` still reached `rfile.read(-1)`, which reads until the client closes and pins a
worker thread for as long as it likes. A negative or unparsable length is a malformed request, not a
large one, and neither should reach the read.
"""

from __future__ import annotations

# A valuation request is a few hundred bytes and an MCP `tools/call` is small. 1 MiB is generous for
# every route either handler serves.
MAX_BODY_BYTES = 1_048_576


def body_too_large(length: object) -> bool:
    """True when a declared `Content-Length` must be refused before the body is read.

    Non-integers and negatives are refused too: `read(-1)` reads to EOF, so a negative length is the
    more dangerous of the two — it exhausts a thread rather than memory.
    """
    if not isinstance(length, int) or isinstance(length, bool):
        return True
    return length < 0 or length > MAX_BODY_BYTES


def too_large_body() -> bytes:
    """The 413 body both handlers send.

    It carries the limit, because "too large" without a number leaves the caller guessing — and the
    two handlers had drifted into different bodies for the same condition.
    """
    return f'{{"error": "Request body too large", "limit_bytes": {MAX_BODY_BYTES}}}'.encode()
