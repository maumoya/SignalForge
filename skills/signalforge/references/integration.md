# Versioned integration

Run `python -m signalforge DATA.json --candidates --out proposals.json`. Output is a JSON object with schema_version `signalforge-candidates/1.0`, `read_only: true`, `no_auto_install: true`, and `candidates`.

Each candidate is a research lead with: stable id, title, category `research-lead`, status `investigate-only`, confidence, a heuristic score, evidence_urls, source `signalforge-offline`, risk `unverified`, and `owner_approval_required: true`.

To integrate with VISION, build a private adapter that validates the schema, treats URL/title as untrusted input, deduplicates against existing Social/Reward Radar entries, and applies VISION's own ROADMAP fit, trust, admission and approval gates. Never write to Social ledgers or Reward Radar state from this external skill directly. Do not include VISION source or private data in this public repository.

Unknown keys can be ignored; schema_version mismatch must fail. Adoption, download, install and execution are outside this interface.
