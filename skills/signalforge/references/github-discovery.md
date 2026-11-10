# Public GitHub discovery (opt-in)

SignalForge v0.1 has two separate modes:

- `python -m signalforge DATA.json` is **fully offline** and works on supplied public video metadata.
- `python -m signalforge.discovery "search terms" --limit 10` explicitly makes one unauthenticated HTTP GET to the **fixed public GitHub API host** (`https://api.github.com/search/repositories`). No token, login, cookies, package installation or third-party runtime dependency. GitHub receives the search query and standard HTTP connection metadata. Never put sensitive information in a query.

Use `--candidates --out research-leads.json` to create a versioned, read-only proposal file. No candidate can trigger code execution, installation or adoption.

Collection safeguards: HTTPS to a hardcoded API endpoint only; redirect refusal; bounded response size (2 MB), timeouts, bounded results (max 20), strict repo URL validation and output no-overwrite semantics. The GitHub API may impose unauthenticated rate limits. The score uses repository stars, forks and activity to rank **research attention**, not quality, novelty, market fit or security. Do not merge these numeric scores with creator-relative video view multipliers.

Downstream verification must inspect maintained commits, dependencies, license, advisories, reproducibility and relevance before ever considering implementation.

All CI tests use in-memory canned API responses; no network requests occur in tests.
