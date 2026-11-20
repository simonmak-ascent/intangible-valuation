"""The body-size cap, asserted at its boundaries.

The cap is the control that stops a client pinning a worker thread by declaring a length it never
sends. It has one implementation (`api/limits.py`) used by both handlers, and these cases are the
ones that decide whether it holds: at the limit, one over, and the negative case that `read(-1)`
turns into read-to-EOF.
"""

from __future__ import annotations

import pytest

from api.limits import MAX_BODY_BYTES, body_too_large


@pytest.mark.parametrize("length", [0, 1, 1024, MAX_BODY_BYTES])
def test_an_ordinary_length_is_accepted(length: int) -> None:
    assert body_too_large(length) is False


@pytest.mark.parametrize("length", [MAX_BODY_BYTES + 1, 10 * MAX_BODY_BYTES])
def test_one_byte_over_the_limit_is_refused(length: int) -> None:
    assert body_too_large(length) is True


@pytest.mark.parametrize("length", [-1, -1024])
def test_a_negative_length_is_refused(length: int) -> None:
    # `rfile.read(-1)` reads until EOF. Refusing it is what stops a slow client holding a thread.
    assert body_too_large(length) is True


@pytest.mark.parametrize("length", ["abc", None, 1.5, True])
def test_a_non_integer_length_is_refused(length: object) -> None:
    # `int(header)` raising was the old path: an uncaught ValueError from `do_POST`.
    assert body_too_large(length) is True


def test_the_two_handlers_share_the_one_constant() -> None:
    # A second copy of this number would drift silently in one of the two services.
    from api import index, mcp

    assert index.MAX_BODY_BYTES == MAX_BODY_BYTES
    assert mcp.MAX_BODY_BYTES == MAX_BODY_BYTES
