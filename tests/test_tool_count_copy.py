"""The tool count the product prints is the count the server serves.

The site claimed "49 MCP tools" in three components, `docs/index.md`, the docs landing page's stat
card and the footer, while `tools/list` returned 14 — and nothing failed, because no check tied the
two together. This is that check.

It has to cover the **shapes** the count is written in, not just the convenient one. The first
version of this file used a single regex that required the number and the label in one run of text;
the docs stat card writes them in two adjacent elements, so it sailed through with "49" still
published. Every shape is listed here, and the stat-card fixture is demonstrated in that shape.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from mcp_server import tool_surface as ts

ROOT = Path(__file__).resolve().parents[1]

# Every tracked file that states how many tools the product has.
COPY_FILES = (
    "app/(en)/mcp/page.tsx",
    "app/(en)/about/page.tsx",
    "components/layout/Footer.tsx",
    "docs/index.md",
    "docs/overrides/main.html",
    "lib/landing.ts",
    "context7.json",
    "public/llms.txt",
    "README.md",
    "server.json",
    "glama.json",
    "mcp_server/README.md",
    "mcp_server/pyproject.toml",
    "api/mcp.py",
    "docs/mcp.md",
)

# "<n> tools", "<n> MCP tools", "<n> valuation tools" in one run of text.
# A short prose gap is allowed, because `public/llms.txt` writes "14 read-only, deterministic MCP
# tools" and the README "14 folded tools". Neither matched the first version, so llms.txt sat in
# COPY_FILES checked by nothing. The gap cannot start on a digit, so "1056 tests and 14 MCP tools"
# still yields 14 only.
INLINE = re.compile(r"(\d+)\s+(?:[A-Za-z][A-Za-z-]*[,\s]+){0,4}(?:MCP\s+)?tools\b", re.IGNORECASE)
# The docs landing page writes `<p class="stat-number">49</p>` and the label in the next element.
STAT_CARD = re.compile(
    r'class="stat-number"[^>]*>\s*(\d+)\s*</p>\s*<p[^>]*class="stat-label"[^>]*>\s*'
    r"(?:valuation\s+)?(?:MCP\s+)?tools\s*</p>",
    re.IGNORECASE,
)
# The landing page's stats array: { value: "14", label: "MCP tools" }.
# zh and hk write the same array as `{ value: "14", label: "个 MCP 工具" }`, which an English-only
# label pattern never matched — so a stale count there would have stayed green.
OBJECT_STAT = re.compile(r'value:\s*"(\d+)"\s*,\s*label:\s*"[^"]*?(?:tools|工具)"', re.IGNORECASE)
# The zh/hk capability line: `"14 个工具 / 124+ 公式"` is a plain array element — no `value:`/`label:`
# keys for OBJECT_STAT, and INLINE requires the ASCII word `tools`. A file-level match was not enough:
# the stats array satisfied this list while the line beside it went unchecked.
CJK_COUNT = re.compile(r"(\d+)\s*[个個]\s*(?:MCP\s+)?工具")
# The README shield: MCP-14%20tools.
BADGE = re.compile(r"MCP-(\d+)%20tools", re.IGNORECASE)


def _claimed_counts() -> dict[str, set[int]]:
    claimed: dict[str, set[int]] = {}
    for rel in COPY_FILES:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        found: set[int] = set()
        for pattern in (INLINE, STAT_CARD, OBJECT_STAT, CJK_COUNT, BADGE):
            found |= {int(n) for n in pattern.findall(text)}
        if found:
            claimed[rel] = found
    return claimed


def test_every_listed_file_is_actually_matched() -> None:
    # A file listed in COPY_FILES that no pattern matches is a check that silently passes — which is
    # how "49" survived in the docs stat card and in llms.txt while this file reported green.
    claimed = _claimed_counts()
    unmatched = [rel for rel in COPY_FILES if (ROOT / rel).exists() and rel not in claimed]
    assert unmatched == [], f"listed in COPY_FILES but no pattern matches: {unmatched}"


def test_at_least_one_surface_states_the_count() -> None:
    # If this fails the patterns or the copy changed shape — not a reason to drop the check silently.
    assert _claimed_counts(), "no file states a tool count any more"


def test_every_printed_count_matches_the_tool_surface() -> None:
    actual = ts.tool_count()
    wrong = {rel: sorted(c) for rel, c in _claimed_counts().items() if c != {actual}}
    assert wrong == {}, f"copy disagrees with tool_count()={actual}: {wrong}"


@pytest.mark.parametrize("rel", COPY_FILES)
def test_no_stale_separate_claim_in_the_copy(rel: str) -> None:
    path = ROOT / rel
    if not path.exists():
        pytest.skip(f"{rel} is not in the tree")
    text = path.read_text(encoding="utf-8")
    for stale in ("49 tools", "49 MCP"):
        assert stale not in text, f"{rel} still claims {stale!r}"
    assert '<p class="stat-number">49</p>' not in text, f"{rel} still has a 49 stat card"
