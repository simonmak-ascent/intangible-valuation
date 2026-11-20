#!/usr/bin/env python3
"""pylaunch — serve a Vercel-style ``BaseHTTPRequestHandler`` module over a
standard-library threaded HTTP server.

All three surfaces of this project expose their hosted endpoint as a Vercel function, i.e. a
``BaseHTTPRequestHandler`` subclass named ``handler``. Vercel's runtime calls it directly; off the
platform this wraps it in ``ThreadingHTTPServer`` — stdlib only, no framework dependency.

    pylaunch --app api.index:handler --host 127.0.0.1 --port 8020

This file lived only in the nodes' work trees until 2026-11-20, which is why the `iv-api` and
`iv-mcp` images could not be built from the repository at all. It is the launcher the container
command already invokes; what committing it changes is that the image can now be built from source,
and that it carries the two bounds below — a 64-slot accept queue and a 30 s per-read timeout — which
the node's copy did not have.
"""

from __future__ import annotations

import argparse
import importlib
from http.server import ThreadingHTTPServer


def load(spec: str) -> type:
    mod_name, _, cls_name = spec.partition(":")
    module = importlib.import_module(mod_name)
    return getattr(module, cls_name or "handler")


class _BoundedServer(ThreadingHTTPServer):
    """A bounded accept queue.

    The attribute must sit on the **class**, not on the instance: ``TCPServer.__init__`` calls
    ``server_activate()``, and that is where ``listen()`` happens — so assigning it after construction
    changes nothing, which is what an earlier version of this file did: the bound it claimed did not
    exist.

    What the socket kept instead is the stdlib default, ``socket.SOMAXCONN`` — 4096 under glibc, not
    the 5 that CPython falls back to only where a platform defines no ``SOMAXCONN``
    (``request_queue_size = getattr(socket, "SOMAXCONN", 5)``). So 64 is a deliberate *lower* bound on
    the accept queue rather than a raise on a default of 5, chosen small because this is one container
    behind an ALB with a health probe. Raise it if a burst ever meets a dropped SYN.
    """

    request_queue_size = 64


def main() -> None:
    ap = argparse.ArgumentParser(description="Serve a BaseHTTPRequestHandler module.")
    ap.add_argument("--app", required=True, help="module:ClassName (default class 'handler')")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, required=True)
    args = ap.parse_args()
    handler = load(args.app)
    # A per-connection read timeout, so a client that opens a socket and says nothing releases its
    # thread. `socketserver` reports the timeout through `handle_error` and frees the worker; without
    # it, this launcher — which serves unauthenticated endpoints — holds the thread indefinitely.
    handler.timeout = 30
    srv = _BoundedServer((args.host, args.port), handler)
    print(f"pylaunch: serving {args.app} on {args.host}:{args.port}", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
