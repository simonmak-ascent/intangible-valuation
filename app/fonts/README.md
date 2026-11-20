# Vendored fonts

Seven woff2 files, latin subset, fetched from the Google Fonts CSS API (`fonts.googleapis.com/css2`)
and committed so that `next build` never opens a TLS connection to a third party.

**Why they are here.** `next/font/google` downloads at build time. On 2026-11-18 a Quality Gate job
sat 31 minutes at 0% CPU holding four `ESTABLISHED` sockets to a Google edge, and no workflow set
`timeout-minutes`, so the default was six hours. A build must not depend on someone else being
reachable, and a font is not worth that coupling.

| file | family | weight | sha256 |
|---|---|---|---|
| `open-sans-300-800.woff2` | Open Sans (variable) | 300–800 | `d8e4fe0452aa2076429a9bb5d8757d00a994dd95986cf950e9a1a371b9a072a0` |
| `raleway-100-900.woff2` | Raleway (variable) | 100–900 | `b1bef1f03a77a36fc257c5525e32a1dd621bb6f935b743a419da7ed0b18dc8f5` |
| `jetbrains-mono-100-800.woff2` | JetBrains Mono (variable) | 100–800 | `18be452724bfdc236c074ca94a249a7f41a86752c7d04ab258ce9ed5651f6a7e` |
| `titillium-web-400.woff2` | Titillium Web | 400 | `861b80b49d2a634d8746e2e45c672309d9ba69a2fdd95da2af034d7a1d09b3f9` |
| `titillium-web-600.woff2` | Titillium Web | 600 | `f356ff5613e1b6789a47ae3bd6b72fa6fb61d44493811bcb758fb4229b7a8bcb` |
| `titillium-web-700.woff2` | Titillium Web | 700 | `9e3162d81ed6681322ab34791660f1b45c79945197e7a7dbb217005b2926caf4` |
| `titillium-web-900.woff2` | Titillium Web | 900 | `c04d7e94b56f110ceb18160aaede8f789c7d8d32740cf74b10ad24d304e6fde8` |

The 900 is not decorative: `components/landing/Landing.tsx` uses `font-black` on the hero heading and
`app/globals.css` forces `font-serif` on `h1`–`h4`, so the stylesheet asks for a weight Titillium Web
does not derive from 700.

All seven are licensed under the SIL Open Font License 1.1, which permits bundling and redistribution:

- Open Sans — © Steve Matteson / Google
- Raleway — © The Raleway Project Authors
- JetBrains Mono — © JetBrains s.r.o.
- Titillium Web — © Accademia di Belle Arti di Urbino

Text: <https://openfontlicense.org>. The licence and the four projects' verbatim copyright notices are
served with the site at `/fonts/OFL.txt` (`public/fonts/OFL.txt`) — OFL 1.1 clause 2 conditions
redistribution on the notice and licence accompanying the Font Software, the repository's root
`LICENSE` is MIT, and the font files are copied into the deployed image, so the licence travels with
them rather than living only in git. Raleway declares a Reserved Font Name; the files here are
unmodified, so that clause is not triggered, and the notice is reproduced as given.

**Regenerating one.** The file must stay byte-identical if you only re-download it; a changed hash
means a changed upstream artefact, which is worth a look rather than a commit. `next/font/local`
parses every file at build time, so an HTML error page in place of a font fails the build instead of
shipping silently.
