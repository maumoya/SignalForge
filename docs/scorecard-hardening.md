# OpenSSF Scorecard hardening — owner settings and reproducible evidence

Verified on 2026-11-09 from the latest `main` GitHub Actions Scorecard logs ([run #42543894709](https://github.com/maumoya/SignalForge/actions/runs/42543894709)), overall **7.0/10**. Primary low/zero checks:

| Check | Score | Remediation |
|---|---:|---|
| Branch-Protection | 0/10 | Turn on an active ruleset on `main` (owner admin setting; not changed by this PR) |
| Code-Review | 0/10 | Require substantive review by another trusted human; self-reviewed/sole-owner merges won't earn this |
| CII-Best-Practices | 0/10 | Register and complete the *real* bestpractices.dev assessment |
| Fuzzing | 10/10 | ClusterFuzzLite workflow now detected by Scorecard; keep it functional and monitored |
| Maintained | 0/10 | Newly created repo (<90 days); needs time |
| Contributors | 3/10 | One contributor organization; don't add fake contributors |
| Signed-Releases | Not scored | A real signed tag/release needed |
| Packaging | Not scored | A published tagged release or supported package distribution needed |

**7.4–8 is an objective, not a claim.** Branch protection and independent code review are the biggest outstanding security gaps. Re-run <https://github.com/maumoya/SignalForge/actions/workflows/scorecard.yml> after admin settings and release; display only the observed value.

## Protect main (repo-owner action)

Use <https://github.com/maumoya/SignalForge/settings/rules> → New ruleset → New branch ruleset:

- Name: `Protect main`; enforcement: **Active**; target: `main` (default branch).
- Block deletions and force pushes.
- Require changes through pull requests.
- Require successful status checks selected from actual recent runs: Tests, Skill lint, CodeQL, Authorship, Dataset action self-test. Verify exact context names in GitHub UI before activating.
- Prefer one *independent* human approval and dismiss stale reviews. **Do not enable an impossible one-review policy for a single-owner repo without a qualified reviewer**: that would block all merges. PR-only with zero required approvals is a usable intermediate control but will not satisfy code-review integrity scoring.
- Do not use a broad bypass role or auto-disable CI checks to inflate a Scorecard result.

After saving, verify GitHub no longer displays `Your main branch isn't protected`, then re-run Scorecard.

## Other owner-only security settings

- <https://github.com/maumoya/SignalForge/settings/security_analysis> → enable private vulnerability reporting if supported.
- <https://www.bestpractices.dev/> → register this repository, answer truthfully, and complete the real passing criteria.
- <https://github.com/maumoya/SignalForge/settings> → add repository description, homepage and five meaningful topics. These improve readiness/discovery, not necessarily OpenSSF.
- Upload an accurate 1280×640 PNG social preview through GitHub Settings → General → Social preview.
- Sign and verify a genuine release tag, then publish the action through GitHub Marketplace.

Why these are owner-only: GitHub connection in this conversation exposes source/PR write operations but not settings/rulesets, tag signing, releases or legal agreements. No change is represented as active unless GitHub confirms it.
