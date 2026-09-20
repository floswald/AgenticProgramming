# Course Redesign Plan — Intro Programming for Econ Masters (AI-native)

12 × 2h sessions + S0 async pre-work. Stack: R and Python, OpenCode as harness (free-tier provider). Working doc, not part of the built site.

## S0 — Accounts & install (async, ~45 min)
**Objective:** every student arrives at S1 with a working terminal, git, and OpenCode talking to a free-tier LLM provider.
**Outcome:** completed checklist in `00-prework.qmd`.
**No live time spent on setup in S1.**

## S1 — Kickoff (in-person)
**Objective:** understand the layered model of AI tools (model / harness / tool / skill) and why "programming" now means supervising an agent, not only writing code by hand. Get comfortable in a shell and initialize a git repo.
**Outcome:** every student has a git repo with a trivial script, committed, and has run one OpenCode session end to end.
**Prereq:** S0.

## S2 — Programming constructs, agent-native (in-person)
**Objective:** learn variable, loop, conditional, function — in both R and Python — by having the agent write a first draft and the student verify/break it. Establish the core habit: "where is this wrong, and how do I check?"
**Outcome:** a small set of equivalent R/Python scripts (same task, both languages), each with a hand-written test the student wrote to catch a bug the agent introduced.
**Prereq:** S1.

## S3 — Git + project config (remote)
**Objective:** version control as agent-compatibility infrastructure — no hardcoded paths, README discipline, clean project layout. Introduce project-level agent config (rules file), model pinning, prompt archiving. Package structure as a reproducibility unit (absorbs old 09-R-packages).
**Outcome:** student's S2 repo restructured to a standard layout with a config file and a README an agent (and a stranger) could pick up cold.
**Prereq:** S2.

## S4 — How do LLMs actually work (in-person)
*(Replaces old 11-NLP-R, whose original purpose — introducing students to language models — is now better served directly. Moved ahead of the harness session: understanding the model comes before understanding tools built on top of it.)*
**Objective:** a simple, non-technical-but-correct lecture on how LLMs work: tokenization, next-token prediction, transformer architecture at a conceptual level, training/RLHF, why hallucination is a structural property and not a bug to be patched away.
**Outcome:** student can explain, at a dinner-party level of rigor, why an LLM confidently states a wrong number.
**Prereq:** S3.

## S5 — How agents work: context, tools, harnesses (in-person)
**Objective:** context windows, attention (conceptual, not math-heavy), tool calling, system prompts — the mechanics of *how an agent operates*, at the systems/harness level, now grounded in the model-internals picture from S4. Live comparison: OpenCode+free model vs Claude Code+paid model on the same task — same task, different cost/quality tradeoff, reinforces model/harness separation.
**Outcome:** student can explain, in their own words, what happens between typing a prompt and a diff appearing on screen.
**Prereq:** S4.

## S6 — Data wrangling: DuckDB (in-person)
**Objective:** SQL, dplyr, Ibis on a real dataset via DuckDB. Agent drafts queries against a dataset with a known answer; student verifies before trusting output.
**Outcome:** working DuckDB pipeline, plus a written note of one case where the agent's first answer was wrong and how the student caught it.
**Prereq:** S5.

## S7 — Testing & verification, part 1: unit tests (remote)
**Objective:** unit testing fundamentals in both R and Python (testthat / pytest), applied directly to the S6 pipeline. What to test, what not to bother testing, arrange-act-assert, fixtures.
**Outcome:** a first test suite covering the S6 pipeline's core transformations.
**Prereq:** S6.

## S8 — Testing & verification, part 2: verification patterns (in-person)
**Objective:** deep dive beyond unit tests — property-based/invariant checks, golden-output comparisons, assertions embedded directly in agent-facing scripts, and systematic checks for silent data decisions and hallucinated numbers. The core question from S7 ("where is this wrong, how do I check?") gets a full toolkit here.
**Outcome:** a test suite that would have caught a deliberately-seeded bug in the S6 pipeline, built without being told where the bug is.
**Prereq:** S7.

## S9 — Cost & model economics (in-person)
**Objective:** token pricing, model tiers, when a cheap/free model is good enough, local vs API tradeoffs, budgeting an agent-driven pipeline for a real research project.
**Outcome:** a cost estimate (tokens, $, time) for running the student's S6 pipeline at 10x and 100x data scale.
**Prereq:** S5, S6.

## S10 — Spatial data, agent-native (in-person)
**Objective:** rework of old 10-spatial-R. Agent proposes CRS transforms and spatial joins; student verifies against a plotted map, since spatial bugs are often silent (wrong projection still "looks like a map").
**Outcome:** a correct choropleth/spatial join the student can explain, including one case they had to correct.
**Prereq:** S2, S5.

## S11 — Reproducibility & failure modes (remote)
**Objective:** JPE-style replication-package standards (your Data Editor lens), tying together the failure modes seen across S4–S10. Debrief: catalogue every place an agent produced a plausible-but-wrong result during the course, and what caught it — cross-reference against the S7/S8 test suites.
**Outcome:** a personal checklist each student writes for their own future agent-assisted work.
**Prereq:** S4, S8.

## S12 — Capstone (in-person)
**Objective:** end-to-end agentic research project on a question of the student's choice, using everything from S1–S11 (git, config, data wrangling, tests, cost awareness).
**Outcome:** short presentation + peer review; project repo meets the S3/S11 reproducibility bar.
**Prereq:** all prior sessions.

---

## Open items
- Old files 01–04 (shell) and 06 (concepts): fold into S1/S2, then decide keep-as-reference vs delete.
- 09-R-packages: absorbed into S3, standalone file likely retired.
- `_quarto.yml` sidebar not yet updated to reflect new session structure — hold until content is drafted.
- WSL2 install instructions salvaged from `2025-09-30-PythonIntro` Jekyll repo, now living in `00-prework.qmd`.
