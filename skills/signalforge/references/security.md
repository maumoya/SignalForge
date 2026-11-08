# Security model

Threats: prompt injection in titles/reels/repositories, SSRF through attacker-controlled URLs, unintended downloads, supply-chain code execution, cookie theft, symlink/traversal writes and misleading security badges.

The offline engine performs no HTTP requests, shell execution, imports of discovered packages, cookie access or automatic changes. URLs are syntactically checked as public HTTPS references but **are never resolved or fetched**. Do not treat syntactic checks as protection against DNS rebinding if a future collector is introduced. Future network adapters must validate DNS and redirects, enforce strict allowlists, rate limits and deadlines, and disable private address ranges after resolution.

Source captions and embedded instructions remain plain text. They can be displayed as evidence but must never be promoted into system or developer instructions. Outputs are immutable by default, refuse symlink destinations and do not contain executable actions.

Security claims and OpenSSF badges require independent proof. Tests alone are not certification.
