# The Editorial Standard

The skill is built on the **Universal Book Writing & Editorial Standard**, a 22-section Bengali guideline for professional book writing, research, storytelling, editing and publication quality. The standard is stored **verbatim** in `skills/book-writer/references/standard/`, split into topic files so Claude loads only the parts a task needs.

## Where each section lives

| File | Sections | Topics |
|---|---|---|
| `01-foundations-and-modes.md` | Preamble, §1-§4 | Purpose and editorial philosophy; scope and genres; instruction priority; context awareness; the 7 writing modes; meaning preservation |
| `02-prose-and-natural-writing.md` | §5-§6 | Prose quality, voice, rhythm, paragraph flow, respect for the reader; anti-formulaic and anti-AI rules; artificial profundity; adjective discipline; emotional authenticity |
| `03-fiction.md` | §7, §15 | Premise, plot logic, character, dialogue, show and tell, POV and tense, pacing, mystery and twist integrity, setting, ambiguity, continuity; genre adaptation rules |
| `04-nonfiction-and-research.md` | §8-§9 | Explanation, fact vs interpretation vs opinion, evidence; no fabricated facts, source reliability and attribution, time-sensitive and unverified information |
| `05-bengali-language.md` | §10 | Standard Bengali, spelling and grammar, Bengali-English balance, register, punctuation (no em dash), dialogue formatting, numbers and dates |
| `06-structure-length-reader-ethics.md` | §11-§14 | Chapter purpose, headings, openings and endings, repetition control, continuity; length and density; reader experience and sensitivity; originality, ethics, copyright |
| `07-quality-control-and-delivery.md` | §16-§22 | Formatting; the editorial QC checklist; change discipline; the final publication test; delivery rules; the 20 non-negotiable rules; the ultimate standard |

The 20 non-negotiable rules (§21) also appear verbatim at the end of `SKILL.md`, so they are always in context.

## Which files a task loads

| Task | Files |
|---|---|
| Every task | 01, 07 |
| Drafting, rewriting, line editing | + 02, 06 |
| Fiction | + 03, `genre-craft.md` |
| Nonfiction | + 04 |
| Bengali text | + 05, `bengali-craft.md` |
| English text | + `english-craft.md` (replaces §10) |
| Multi-chapter projects | + `long-form-workflow.md` |

## The standard vs the additions

The files in `references/standard/` are the user's original text. Everything else in `references/` was written for this skill to fill gaps in the standard, and **never overrides it**:

| Addition | What it adds |
|---|---|
| `bengali-craft.md` | House style defaults; high-frequency প্রমিত spelling points (কী/কি, কোন/কোনো, মতো/মত, পড়া/পরা, চন্দ্রবিন্দু); আপনি/তুমি/তুই verb agreement and kinship terms; সাধু/চলিত/dialect; 10 translationese patterns; Bengali stock phrases; typography; dialogue; rewriting sentences without the em dash |
| `english-craft.md` | §10 adapted for English: spelling variety, quotes, numbers, taka and lakh/crore, English AI tells, dialogue, nonfiction voice |
| `genre-craft.md` | Mystery (fair play), Thriller, Horror (Bengali folk horror), Romance, Adventure (real geography), Religious (Quran/hadith citation integrity), Children's/YA |
| `long-form-workflow.md` | Project layout, chapter-by-chapter sequence, and templates for book brief, story bible, chapter plan, continuity ledger, fact ledger, editorial notes and review report |

## Editing the rules

The topic files in `references/standard/` are the **canonical copy** of the standard. To change a rule, edit it there.

- **Keep section numbers stable.** `SKILL.md`, the craft files and the checker's messages cite rules by number (e.g. §10.5, §21.10).
- **When you add a new section** (e.g. `## 23. …`), put it in the topic file it belongs to and add a row to the "Which files a task loads" table in `SKILL.md`, section 4, if a mode needs it.
- **If you change §21,** update the verbatim copy at the end of `SKILL.md` too.
- **If you change a rule the checker enforces** (em dash, digits, spelling variants), update the matching list in `scripts/check_manuscript.py`.
