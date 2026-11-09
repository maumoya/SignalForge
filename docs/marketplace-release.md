# GitHub Marketplace publication — owner steps

This is a GitHub **Action** (`action.yml` at the repo root) and a **Claude Code plugin/Agent Skill**. Listing the GitHub Action in GitHub Marketplace does not automatically list the Claude plugin in Anthropic's marketplace. Both are separate distribution channels.

## Verified readiness
- Public repo `maumoya/SignalForge`; root `action.yml` exists and passed its positive/negative CI self-test.
- Action metadata: `SignalForge dataset check`, author `Mauricio Moya`.
- Owner has GitHub's **Draft a release** banner (confirmed in screenshot).
- No GitHub Marketplace listing, published tag, signed release, Best Practices award or external LLM installation test has been verified yet.

## Publish the action
1. Open <https://github.com/maumoya/SignalForge/blob/main/action.yml> and select **Draft a release** (or visit <https://github.com/maumoya/SignalForge/releases/new>).
2. Select **Publish this Action to the GitHub Marketplace**; GitHub validates name uniqueness.
3. Accept the **GitHub Marketplace Developer Agreement** if prompted. This is the owner's legal decision, not something an automation should accept.
4. Select primary category (suggestion: **Code quality**) and optional secondary category, if offered.
5. Create a **versioned signed and GitHub-Verified tag** through an authenticated signing environment; do not claim a signed tag from a button that creates an unsigned tag. Check repository release workflow's tag contract before publishing.
6. Title: `SignalForge v0.1.0 — Public Metadata Triage`.
7. Description must emphasize supported features: offline video JSON analytics, optional public GitHub search, read-only findings, CI-tested dataset Action. Do **not** claim automatic reel ingestion, malware scanning, 50h watched, human time savings, or full VISION integration.
8. Confirm the action name is unique and all published categories/terms/2FA requirements. Publish through GitHub's owner UI, then verify the live Marketplace URL and a real install from the tagged version.

**Release blocker:** the current release workflow prepares SLSA provenance for annotated tags but does *not* cryptographically sign tags on behalf of the owner. Owner signature verification must be completed separately.

GitHub documentation: <https://docs.github.com/en/actions/how-tos/create-and-publish-actions/publish-in-github-marketplace>.
