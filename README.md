# Book Writer Skill · বই লেখার স্কিল

An [Agent Skill](https://agentskills.io) that makes Claude write and edit books in **Bengali (বাংলা)** and **English** to the standard of a professional publisher. It follows the *Universal Book Writing & Editorial Standard*, a 22-section editorial guideline for prose that reads as written by a skilled author rather than assembled by a machine.

> **লক্ষ্য কেবল মানুষের মতো শোনানো নয়। লক্ষ্য এমন একটি বই তৈরি করা, যা নিজস্ব ভাষা, চিন্তা, কল্পনা, গবেষণা ও সম্পাদনার মানে পাঠকের আস্থা এবং আগ্রহ অর্জন করে।**

## What it does

- **Seven editorial modes**, each with its own limits: ideation, research & planning, drafting, developmental editing, rewriting & line editing, copyediting & proofreading, and fact-checking. A "polish this" request never comes back with a new subplot.
- **The full editorial standard, verbatim.** All 22 sections in the original Bengali, split by topic so Claude loads only what each task needs.
- **Bengali craft:**
  - প্রমিত spelling (কী/কি, কোন/কোনো, মতো/মত, বাড়ি not বাড়ী)
  - আপনি/তুমি/তুই verb agreement
  - সাধু/চলিত consistency and dialect in dialogue
  - 10 translationese patterns to avoid
  - typography: `।`, Bengali digits, no em dash
- **English craft:** the same standard adapted for English, including a catalog of AI-sounding words and constructions.
- **Genre craft:** Mystery (fair-play clues), Thriller, Horror (Bengali folk horror), Romance, Adventure (real geography), Religious (no fabricated Quran or hadith quotes), Children's/YA.
- **Long-form workflow:** a book brief, story bible, chapter plan and continuity ledger that keep names, clues and timelines consistent across a whole novel.
- **Manuscript checker:** a dependency-free Python script that flags em dashes, `.` instead of `।`, সাধু-চলিত mixing, non-standard spellings, inconsistent spellings, stock AI phrases, contrast templates, uniform sentence rhythm, repetition and more.
- **No invented facts.** Statistics, studies, quotations, citations and case studies are never fabricated. Anything unverifiable is flagged outside the manuscript.

## Quick install

**Claude Code**

```text
/plugin marketplace add akr4m/book-writer-skills
/plugin install book-writer@book-writer-skills
```

**Claude.ai:** zip `skills/book-writer`, then go to **Customize → Skills → + → Create skill → Upload a skill** (code execution must be on).

**Codex, Copilot CLI, Cursor, OpenCode, Gemini CLI**

```bash
git clone https://github.com/akr4m/book-writer-skills.git
mkdir -p ~/.agents/skills && cp -R book-writer-skills/skills/book-writer ~/.agents/skills/
```

**Claude API and Agent SDK:** see the installation guide.

**→ [Full installation guide](docs/installation.md)** covers every platform, Windows, updates and troubleshooting.

## Example prompts

```text
আমাদের ইবুক প্ল্যাটফর্মের Mystery ক্যাটাগরির জন্য একটা মৌলিক ছোটগল্প লিখে দাও, ২০০০ থেকে ২৫০০ শব্দ।
প্রেক্ষাপট সিলেটের একটা পুরোনো চা-বাগান, ভরা বর্ষা। third person। শেষে যুক্তিসংগত সমাধান চাই।
```

```text
chapter2_draft.md পড়তে AI-এর লেখার মতো লাগছে। আরও natural করে দাও, কিন্তু ঘটনা বা অর্থ বদলাবে না।
```

```text
Write the opening chapter (~1,500 words) of a personal finance book for fresh graduates in
Bangladesh earning 25-40k taka a month. Warm, practical, not preachy.
```

**→ [Usage guide](docs/usage.md)** has examples for every mode, including planning a full novel, review, and fact-checking religious references.

## How it works

```
request ─► language (asked > manuscript > request)
        ─► mode (ideation · planning · drafting · developmental · line edit · proofread · fact-check)
        ─► load only the rule files that mode needs
        ─► write / edit
        ─► run check_manuscript.py ─► fix every ERROR, judge every WARN
        ─► editorial review (§17) + publication test (§19)
        ─► deliver: manuscript only in the file; notes outside it
```

## Repository layout

```
book-writer-skills/
├── .claude-plugin/
│   └── marketplace.json          Claude Code plugin marketplace manifest
├── skills/
│   └── book-writer/              ← the skill (copy this folder to install it manually)
│       ├── SKILL.md              router: language, mode, reading map, check, delivery, §21 rules
│       ├── references/
│       │   ├── standard/         the editorial standard, verbatim (§1-§22, 7 topic files)
│       │   ├── bengali-craft.md
│       │   ├── english-craft.md
│       │   ├── genre-craft.md
│       │   └── long-form-workflow.md
│       ├── scripts/
│       │   └── check_manuscript.py
│       └── evals/                test prompts and assertions (not needed at runtime)
└── docs/
    ├── installation.md
    ├── usage.md
    ├── checker.md
    └── editorial-standard.md
```

## The manuscript checker

```bash
python3 skills/book-writer/scripts/check_manuscript.py manuscript/*.md
```

```
ERROR  em-dash (3): Em dash or a dash used like one (§10.5, §21.10) ...
WARN   sadhu-in-cholit (2): সাধু forms in চলিত prose (গুরুচণ্ডালী) ...
WARN   nonstandard-spelling (4): ... প্রমিত form uses ি (বাড়ি, তৈরি, খুশি, সরকারি ...)
WARN   ai-cliche (7): Stock or AI-like expression (§6.2) ...
-- 1 error(s), 4 warning(s)
```

It exits with code 1 when there are errors, so it fits pre-commit hooks and CI. **→ [Checker reference](docs/checker.md)** lists every check, `--json` output and house-style customization.

## Editing the rules

The standard lives in `skills/book-writer/references/standard/`, and those files are the canonical copy. Edit a rule there, and keep the section numbers (§10.5, §21.10) stable, because the skill and the checker cite them. **→ [Editorial standard map](docs/editorial-standard.md)**

## Evaluation

The skill was tested on three tasks, each run with and without the skill (Claude Opus 5.5, one run per configuration, so treat the numbers as directional):

| Task | With skill | Without skill |
|---|---|---|
| Bengali mystery short story (2,000-2,500 words) | 14/14 | 13/14 (em dashes) |
| Bengali "make it natural" rewrite of an AI-sounding draft | 13/13 | 13/13 |
| English personal-finance opening chapter | 11/11 | 9/11 (unlabelled invented case study, blog-style headings) |
| **Pass rate** | **100%** | **92%** |

Beyond the scores, with the skill the rewrite cut an artificially profound line and told the author, instead of silently rewording it. The cost is about 1.9× the tokens and 1.6× the time, mostly from reading the reference rules. The prompts and assertions are in [`skills/book-writer/evals/evals.json`](skills/book-writer/evals/evals.json).

## Contributing

Issues and pull requests are welcome, especially:
- additional Bengali stock phrases and translationese patterns
- dialect notes
- genre craft for categories not yet covered
- false positives from the checker

Please keep changes to `references/standard/` faithful to the standard's intent, and run the checker on the eval files before submitting.
