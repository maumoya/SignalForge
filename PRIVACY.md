# Privacy — SignalForge

SignalForge has two separate execution modes.

**Offline video analysis:** `python -m signalforge DATA.json` reads local metadata, computes a report and optionally writes a new JSON file. It does not make HTTP requests, use hosted AI models, collect cookies, request credentials, send telemetry or run in the background.

**Opt-in public GitHub discovery:** `python -m signalforge.discovery "public search terms"` makes one unauthenticated HTTPS request to the fixed `api.github.com` search endpoint. GitHub receives the **search phrase**, IP address and ordinary connection metadata; the public repository results are returned to your machine. No GitHub personal access token, OAuth, private repository data or local video dataset is sent. Don't put secrets in queries. The endpoint has rate limits. No redirect is followed and response size and result count are bounded. The command does not run code from any returned repository.

If invoked inside another agent, that agent's own settings determine whether your messages are sent to its provider. The no-cloud-model statement describes SignalForge itself, not any connected host agent.

Maintainer: **Mauricio Moya** · [GitHub](https://github.com/maumoya).
