# Long-form Workflow and Templates

For any work that spans several chapters or sessions. Across a long book a writer loses track of names, ages, clues and promises unless they are written down. These files are the project's memory. They also put §2.3 into practice: an approved brief, outline and bible outrank the general standard. They support §7.11 (fictional continuity) and §11.5 (book-wide consistency).

## Project layout

When you can write files, keep a project folder like this. If the user already has a structure of their own, use theirs.

```
<book-slug>/
  00-brief.md            Book Brief, approved by the user
  01-bible.md            Story Bible (fiction) or Research & Fact Ledger (nonfiction)
  02-chapter-plan.md     One entry per chapter
  03-continuity.md       Running ledger, updated after every chapter
  manuscript/
    01-<slug>.md         One file per chapter, manuscript text only
  editorial-notes.md     Open issues, verification needed, recommendations
```

## Sequence

1. **Brief.** Settle the critical unknowns: language, genre, audience, length, POV and tense, ending type (fiction), and purpose (nonfiction). Propose defaults the user can accept in a single reply; don't send a questionnaire. Write the brief once agreed.
2. **Bible or research.**
   - Fiction: characters, places, timeline, the rules of the world, and the clue plan for a mystery.
   - Nonfiction: every factual claim you plan to use, with its source and status (verified or needs verification).
3. **Chapter plan.** For each chapter: its purpose (§11.1), what has changed by its end, the POV, and the target length. Note the planned opening and ending mode for each chapter (scene, dialogue, image, summary, time-jump) so they don't repeat by accident (§11.3).
4. **Draft one chapter at a time.**
   - Before each chapter, reread the brief, that chapter's plan entry, the continuity ledger, and the last page of the previous chapter.
   - After each chapter, update the ledger and run `scripts/check_manuscript.py` on the chapter.
5. **Book-wide passes.** Every few chapters and at the end:
   - Run the checker on all chapter files together. It then checks repetition and spelling consistency across the whole book.
   - Do a developmental read (§3.4, §17).
6. **Final manuscript.** Deliver clean text with no notes. Report plainly what is finished and what isn't (§20).

## Length

A target word count is a frame, not a quota (§12.1). If the material is complete short of the target, say so instead of padding. If it needs more room, say that too. When the user gives no length for a chapter, choose one that fits its purpose and state it in your reply.

## Templates

### Book Brief

```markdown
# Book Brief: <working title>
- Language and variety: (e.g. প্রমিত চলিত বাংলা, Bangladeshi readers)
- Category / genre / subgenre:
- Target readers and age:
- Promise to the reader: (fiction: the experience; nonfiction: what the reader will understand or be able to do)
- Premise (fiction) or central argument (nonfiction), in 2-3 sentences:
- Narrative voice, POV, tense:
- Tone and mood:
- Length: (whole book; per chapter)
- Must include / must avoid:
- Ending type (fiction):
- Sources and research base (nonfiction):
- Format and publishing constraints:
- Open questions:
```

### Story Bible

```markdown
# Story Bible
## Characters
### <Name> (role)
- Age, occupation, where they live:
- Speech: register, dialect, verbal habits; who they call আপনি / তুমি / তুই
- Wants / fears / contradiction:
- Arc (if any):
- What they know, by chapter:
## Places
## Timeline
## World rules (supernatural, technology, institutions)
## Clue plan: clue → where planted → what it seems to mean → what it really means
## Motifs: deliberate repetitions, so the checker's repetition flags can be judged
```

### Chapter plan entry

```markdown
## Chapter N: <working title>
- Purpose (what this chapter gives the reader):
- POV / time / place:
- What has changed by the end:
- Opening mode / ending mode:
- Clues planted; threads opened or closed:
- Target length:
```

### Continuity ledger (update after every chapter)

```markdown
## After Chapter N
- New facts established (names, ages, dates, places, objects):
- Who knows what now:
- Threads opened / closed:
- Prominent images and phrases used (don't reuse):
- Departures from the plan, and why:
```

### Fact ledger (nonfiction)

```markdown
| # | Claim as it will appear | Source (author, title, year, page or URL) | Status: verified / needs verification / removed | Chapter |
|---|---|---|---|---|
```

### Editorial notes

```markdown
- [Ch 3, ¶5] Claim "…" needs a source; currently phrased qualitatively.
- [Ch 7] Nadia is 24 here and 26 in Ch 2. Kept 24; please confirm.
```

### Review report (developmental editing or review)

List findings in order of importance. Each one gives:
- the location
- the problem
- why it matters to the reader
- a concrete suggestion

End with a short note on what already works and should be left alone.
