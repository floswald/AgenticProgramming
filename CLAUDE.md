# AgenticProgramming

Quarto website: intro-to-programming course, being redesigned for the AI/agentic era. Taught by Florian Oswald at multiple institutions (currently UniTo ESOMAS) — keep content institution-agnostic.

## State

Mid-migration from old "Intro Programming" (shell/git/R basics) to "Agentic Programming" (still covers core constructs, but centers on agent-assisted workflows, LLM internals, testing/verification, cost, reproducibility).

- Full redesign plan: `course-redesign-plan.md` — objective/outcome/prereq per session, S0–S12.
- Tracking: GitHub milestone "Agentic redesign", one issue per session + 5 infra issues, repo `floswald/AgenticProgramming`.
- Working branch: `agentic-redesign`.
- Old numbered files (`01-shell-intro.qmd` … `11-NLP-R.qmd`) are being folded into new sessions or retired per the plan — don't assume they reflect current course structure. Check `course-redesign-plan.md`'s file-mapping table before editing them.

## Conventions

- Format: Quarto project, `_quarto.yml` at root. Slides use `floswald/quarto-revealjs-clean` extension (`format: clean-revealjs`) — migrating off `metropolis-theme`, don't add new content to the old theme.
- Narrative/doc pages (not slides) set `format: html` in their own frontmatter, overriding the project default. Example: `00-prework.qmd`.
- Shared format options (logo, footer, highlight-style, chalkboard) belong in `_quarto.yml`, not repeated per-file — that's the whole point of the template migration, don't reintroduce per-session format blocks.
- Harness taught in-course is **OpenCode**, not Claude Code — deliberate, so students aren't blocked by needing a paid Anthropic subscription. Claude Code appears only as a one-off paid-tier comparison demo (S5).
- `*_cache/` (Quarto render caches) are gitignored — don't commit them.

## Workflow

- Make incremental commits on `agentic-redesign`, not directly on `main`.
- New/reworked session content should match the objective/outcome/prereq already defined for that session in `course-redesign-plan.md` — check there before inventing scope.
- When a session's content is finalized, close the corresponding GitHub issue and update `_quarto.yml` sidebar (tracked separately in the sidebar-restructure infra issue — don't do it piecemeal per session).

## Parallel issue work: branch-per-issue, implementer/verifier pairs

Every issue in the "Agentic redesign" milestone (#1–18) has its own branch, already cut off `agentic-redesign` via `gh issue develop`, named `<issue-number>-<slug>` (e.g. `5-s4-how-do-llms-actually-work`). Each issue is worked by two agents:

- **Implementer**: runs in an isolated git worktree on that issue's branch (`isolation: "worktree"`). Works until the issue's stated objective/outcome is met. Does **not** open a PR — stops and reports done.
- **Verifier**: spawned fresh (no shared context with the implementer — it must not just rubber-stamp its own prior work) against the same branch. Checks the diff against the issue body, not against vibes. For session-content issues (#1–13): does it meet the stated objective/outcome, does it stay in scope (doesn't silently absorb another session's material), does `quarto render` succeed on the touched file(s) — this is editorial review more than code review. For infra issues (#14–18): actual code review — did the change break rendering elsewhere, does it match the issue's checklist. If it passes, the verifier opens a PR into `agentic-redesign` (never into `main` directly, never auto-merged) and reports back. Florian merges by hand.

**Launch order matters — do not run all 18 at once.** #14/#15 change the format contract (`quarto-revealjs-clean` adoption, centralized `_quarto.yml` config) that every session file's frontmatter depends on; #17/#18 are integration/cleanup that assume session content already exists. Stage it:

1. Infra foundation first: #14, #15, #16 (independent of each other, can run in parallel).
2. Session content once #14/#15 have merged: #1–13, genuinely parallel (mostly disjoint files — verify no two touch the same old file, e.g. #4 and #18 both touch `05-git.qmd`/`09-R-packages.qmd` territory, coordinate those two by hand rather than launching blind).
3. Integration last, after #1–13 have merged: #17 (sidebar restructure), #18 (retire old files).
