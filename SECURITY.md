# Security Policy

SignalForge is an offline, local-first data analysis skill. Public source data, video titles, captions, repositories and documents must always be treated as **untrusted input**, never as instructions for an AI agent.

## Supported versions

Security fixes are applied to the latest maintained release. Version 0.1.0 is a pre-release; the `main` branch is an active development target and is not a signed release.

## Reporting vulnerabilities privately

**Do not open a public issue containing a working exploit, credentials, private data or other sensitive technical details.** Prefer GitHub's private vulnerability reporting under [Security → Advisories](https://github.com/maumoya/SignalForge/security/advisories) when available. If private reporting is unavailable, use the contact method on the [maintainer's GitHub profile](https://github.com/maumoya) and ask for a secure communication channel before sharing sensitive details.

A useful report includes the affected version and commit, potential impact, a minimal reproducible example, and whether a fix or mitigation is known. Use synthetic data only.

## Coordinated disclosure process

The maintainer should acknowledge a privately submitted report as soon as practical and target an initial response within seven days. Triage considers severity, exploitability, impact on local files and credentials, and the possible effects of prompt injection. The aim is to coordinate a fix and release before public disclosure; an exact remediation deadline cannot be guaranteed.

No researcher should ever be asked to run untrusted code to validate a report. Please allow reasonable time to investigate before publishing exploitation details.

## Security boundaries

- The provided Python runtime never makes HTTP requests or executes content from an input dataset.
- It performs no automatic installation, authentication, scheduled execution or modification of external repositories.
- URL validation is **syntactic only**: if a future network collector is implemented, it must defend against DNS rebinding and malicious redirects after DNS resolution.
- Read-only research leads cannot trigger adoption, code installation or owner approval.
- Never collect browser cookies, local secrets, private DMs, or credentials.
- CI pass, a high OpenSSF score, and unit tests are not guarantees of malware-free operation.

See [skill threat model](skills/signalforge/references/security.md).
