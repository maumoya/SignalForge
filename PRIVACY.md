# Privacy — SignalForge

The current v0.1 Python core runs entirely offline. It reads a local JSON file, computes summaries and, if requested, writes a new JSON report. It does not make HTTP requests, upload data, track usage, request account access, collect cookies, fetch videos, send telemetry, or invoke a hosted model. It does not run in the background.

Inputs can include URLs, creator names, titles and topics. Such inputs are untrusted and must be supplied lawfully; never include private messages, access tokens or personal secrets in public examples. If you use SignalForge through Claude Code or a third-party agent, the agent's **own** settings and connections govern whether information is sent to its provider. This privacy statement describes the SignalForge Python engine only.

Future network collectors, if added, will require separate documentation, safe defaults, source restrictions and user consent where appropriate.

Maintainer: **Mauricio Moya** · [GitHub](https://github.com/maumoya).
