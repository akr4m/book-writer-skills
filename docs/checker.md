# Manuscript Checker

`skills/book-writer/scripts/check_manuscript.py` mechanically checks a Bengali or English manuscript against the parts of the editorial standard that a script can verify reliably. The skill runs it automatically before delivering any manuscript, and you can also run it on your own drafts.

It uses only the Python 3 standard library (Python 3.8+), so there is nothing to install.

> The checker catches what is easy to miss by eye in long text. It does **not** judge quality. Meaning, voice, causality, continuity and whether a scene earns its length are left to the editorial review in §17 and §19 of the standard.

## Usage

```bash
# One file
python3 skills/book-writer/scripts/check_manuscript.py chapter-01.md

# A whole book: also adds a book-wide repetition and spelling-consistency pass
python3 skills/book-writer/scripts/check_manuscript.py manuscript/*.md

# From stdin
cat draft.md | python3 skills/book-writer/scripts/check_manuscript.py -

# Force the language (default: auto-detected from the script used)
python3 skills/book-writer/scripts/check_manuscript.py draft.md --lang bn

# Machine-readable output, e.g. for CI
python3 skills/book-writer/scripts/check_manuscript.py draft.md --json
```

**Exit code:** `1` if any ERROR is found, `0` otherwise, so you can use it in a pre-commit hook or a CI job.

## Severities

| Severity | Meaning |
|---|---|
| **ERROR** | Breaks a hard rule of the standard. Fix it. |
| **WARN** | Usually a problem, but legitimate in context (dialogue, period voice, a deliberate motif). Decide case by case. |
| **INFO** | Statistics and single occurrences worth knowing about. |

## Example output

```
== chapter2_draft.md  [bn, 236 words, 25 sentences, 7 paragraphs, sentence length mean 9.4 / variation 0.46]
ERROR  em-dash (3): Em dash or a dash used like one (§10.5, §21.10). Restructure with comma, colon, ...
         L3: অনুভূতি হলো। রাজশাহী স্টেশনটা — যেটা সে তিন বছর আগে শেষবার দে
WARN   sadhu-in-cholit (2): সাধু forms in চলিত prose (গুরুচণ্ডালী) unless intentional ...
WARN   nonstandard-spelling (4): Non-standard ঈ spelling in a non-tatsama word ...
WARN   ai-cliche (7): Stock or AI-like expression (§6.2). Replace with a specific observation, or cut.
WARN   contrast-template (2): Repeated contrast template (শুধু X নয়, বরং Y / not X but Y) (§6.2).
-- 1 error(s), 4 warning(s)
```

## What it checks

### Hard rules (ERROR)

| Check | Rule | Notes |
|---|---|---|
| `em-dash` | §10.5, §21.10 | Flags `—`, `―`, `⸺`, `⸻`, and the look-alikes people substitute for them: a spaced hyphen or en dash between words (`a - b`, `a – b`), `word--word`, and `word–word`. List bullets, Markdown table rules (`\|---\|`) and number ranges (`10–12`) are not flagged. |
| `placeholder` | §20 | `[TODO]`, `TK`, `TBD`, `XXX`, `???`, `[insert …]`, `[… লিখুন]` left in the text. |
| `ascii-full-stop` | §10.5 | An English `.` ending Bengali text. This is an ERROR when the text mostly uses `।`, otherwise a WARN. Standard abbreviations are allowed: ড. ডা. মো. মুহা. পৃ. (সা.) (রা.) (আ.) (রহ.) and others. |

### Bengali language (§10)

| Check | What it flags |
|---|---|
| `ascii-digits` | English digits in Bengali prose. Digits inside quoted English text (e.g. an English ledger entry) are skipped. |
| `space-before-punct` / `no-space-after-punct` | `কথা ।`, `কথা ,` / `কথা।তারপর` |
| `double-danda` | `।।` |
| `sadhu-in-cholit` | সাধু pronouns and verbs (তাহার, যাহা, করিয়া, হইল, বলিল …) in চলিত prose, i.e. গুরুচণ্ডালী |
| `nonstandard-spelling` | ঈ in non-tatsama words where প্রমিত uses ি: বাড়ী, গাড়ী, তৈরী, খুশী, সরকারী, দাবী, বেশী, কাহিনী, ইংরেজী … |
| `inconsistent-spelling` | The same word spelled two ways in one manuscript: করল/করলো, এখনো/এখনও, দেওয়া/দেয়া, ওপর/উপর, সঙ্গে/সাথে … |

### Natural writing (§5, §6, §13)

| Check | What it flags |
|---|---|
| `ai-cliche` | Stock phrases: the §6.2 list plus common additions in Bengali (এক অদ্ভুত অনুভূতি, সময় যেন থমকে, বলাই বাহুল্য …) and English (delve into, tapestry, it's important to note, little did she know …). |
| `contrast-template` | "শুধু X নয়, বরং Y", "একদিকে … অন্যদিকে", "not just X but Y", "it's not X, it's Y". One occurrence is INFO; two or more is WARN. |
| `transition-led-paragraphs` | Three or more paragraphs opening with a stock transition (অন্যদিকে, এছাড়াও, সুতরাং … / Moreover, Furthermore …). |
| `intensifiers` | Any intensifier from §6.4 used three or more times (অত্যন্ত, অসাধারণ, গভীর … / very, crucial, pivotal …). |
| `pressure-phrasing` | Three or more instances of §13.2 phrasing (আপনাকে অবশ্যই, মনে রাখবেন … / you must, starting today …). |
| `uniform-rhythm` | Sentence-length variation below 0.35 across 15 or more sentences. Typical human prose is above 0.45. |
| `uniform-paragraphs` | Paragraph-length variation below 0.25 across 8 or more paragraphs. |
| `repeated-phrases` | 4-word phrases used three or more times. |
| `repeated-openings` | Several paragraphs that open with the same two words. |

### Punctuation and formatting (§10.5, §10.6, §11.2, §16, §18.4)

| Check | What it flags |
|---|---|
| `exclamations`, `ellipses` | More than 4 per 1,000 words (with at least 3 present). |
| `ellipsis-style`, `quote-style` | `…` mixed with `...`; curly quotes mixed with straight quotes. |
| `bengali-digits` | Bengali digits in English text. |
| `heading-density` | More than 3 headings per 1,000 words, which reads like a blog or report. |
| `bullet-prose` | More than 15% of lines are list items. |
| `bold` | More than 5 bold spans. |
| `inline-note` | `Note:`, `নোট:`, `সম্পাদকীয় নোট:` lines inside the manuscript. |

### Book-wide pass (several files)

When you pass several files, a final **BOOK-WIDE** report runs `repeated-phrases`, `repeated-openings` and `inconsistent-spelling` across all of them together (§11.4, §10.2).

## Customizing for your house style

Every word list lives at the top of the script:

| Constant | Purpose |
|---|---|
| `VARIANT_PAIRS` | Spelling pairs checked for consistency. The **left** form is the house default. Swap a pair to change the preference, and update the matching row in `references/bengali-craft.md` §1 too. |
| `NONSTANDARD_II` | ঈ spellings treated as non-standard. |
| `CLICHES_BN`, `CLICHES_EN` | Stock-phrase regexes. |
| `TRANSITIONS_*`, `INTENSIFIERS_*`, `PRESSURE_*` | Lists for the corresponding checks. |
| `BN_ABBREV` | Abbreviations allowed to end in `.` |

Text inside fenced code blocks, inline code and YAML front matter is ignored.
