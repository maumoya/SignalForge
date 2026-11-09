# Input fuzzing (ClusterFuzzLite + Atheris)

SignalForge accepts untrusted strings, URLs, JSON arrays, metadata and video titles. Fuzzing generates unexpected inputs to detect crashes, parser bugs and invariants violated at its trust boundary.

- Targets: `clean_text`, `safe_url` and `load_items` under `signalforge/core.py`.
- Toolchain: Google ClusterFuzzLite with Atheris in an ephemeral pinned OSS-Fuzz Python builder; **CI only**, not a runtime dependency.
- On PRs changing the parser or fuzz config, fuzz for **90 seconds** per run, in addition to Docker build/setup. Weekly batch fuzzing budgets **600 seconds** and does not need a personal token. A job timeout prevents unbounded resource use.
- Results are only counted after the actual GitHub job succeeds; an installed workflow or a Scorecard badge is not proof no vulnerabilities exist.
- Code from untrusted repository search results is **never** executed or installed; the fuzzer runs only our known local parser source.
- Any crashes should yield a minimal reproducer and a regression test before a release. Never hardcode or suppress crashing seeds simply to improve a Scorecard number.
- The Fuzzing check in OpenSSF is expected to detect a genuine ClusterFuzzLite integration, but **the Scorecard result must be re-measured** after merging.

Source: <https://google.github.io/clusterfuzzlite/running-clusterfuzzlite/github-actions/>.
