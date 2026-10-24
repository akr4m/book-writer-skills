# Using the Book Writer Skill

Once the skill is installed, you don't need to call it by name. Ask for book work in Bengali or English and Claude loads it automatically. To force it in Claude Code, type `/book-writer` followed by your request.

## How the skill decides what to do

1. **Language.** It writes in the language you ask for. Otherwise it uses the language of the manuscript, and failing that, the language of your request. Romanized Bengali (`ekta golpo lekho`) produces Bengali script.
2. **Mode.** Each mode permits different changes. This keeps a "polish" request from coming back with a new subplot.

   | You say… | Mode | What changes |
   |---|---|---|
   | ধারণা দাও, title ideas, premise options | Ideation | Genuinely different options, each with its weak point |
   | outline, character bible, chapter plan | Research & planning | Brief, bible, plan, fact ledger |
   | লেখো, write chapter 3 | Drafting | New prose inside the approved story world |
   | এটা কি কাজ করছে?, review my manuscript | Developmental editing | Prioritized findings; major changes recommended, not imposed |
   | সম্পাদনা করো, আরও natural করো, human-written করো | Rewriting & line editing | Better sentences and flow; nothing new added |
   | প্রুফ দেখো, বানান ঠিক করো | Copyediting & proofreading | Smallest correct changes |
   | fact-check, consistency check | Fact-checking | A report of claims, problems and the verification needed |

3. **Rules.** It reads only the parts of the editorial standard the task needs (see [editorial-standard.md](editorial-standard.md)).
4. **Check.** It runs the [manuscript checker](checker.md), then does the §17 editorial review and the §19 publication test itself.
5. **Delivery.** The manuscript file contains only the manuscript. Notes, assumptions and verification requests go in the chat reply, or in `editorial-notes.md` for long projects.

## Example prompts

### Drafting fiction (Bengali)

```text
আমাদের ইবুক প্ল্যাটফর্মের Mystery ক্যাটাগরির জন্য একটা মৌলিক ছোটগল্প লিখে দাও,
২০০০ থেকে ২৫০০ শব্দ। প্রেক্ষাপট সিলেটের একটা পুরোনো চা-বাগান, ভরা বর্ষা।
প্রধান চরিত্র তৃষা, ঢাকার তরুণ সাংবাদিক। third person। শেষে যুক্তিসংগত সমাধান চাই।
markdown ফাইলে সেভ করো।
```

### Making a draft read naturally (Bengali)

```text
chapter2_draft.md ফাইলের লেখাটা AI-এর মতো লাগছে। আরও natural আর human-written করে দাও,
কিন্তু ঘটনা, তথ্য বা অর্থ কিছু বদলাবে না। আলাদা ফাইলে সেভ করো।
```

Your original file is left untouched, and the edit goes to a new file. If a fix would change meaning (for example, cutting a line that might be your theme), Claude tells you and offers to restore it.

### Proofreading only (Bengali)

```text
manuscript/ ফোল্ডারের সব অধ্যায় প্রুফ দেখো। শুধু বানান, যতিচিহ্ন আর সামঞ্জস্য।
ভাষা বা বাক্য বদলাবে না।
```

### Nonfiction chapter (English)

```text
Write the opening chapter (~1,500 words) of a personal finance book for fresh graduates
in Bangladesh earning 25-40k taka a month. Warm, practical, not preachy. Save as markdown.
```

Claude won't invent statistics or case studies. Illustrative numbers are labelled as examples, and anything that needs a source is flagged outside the chapter.

### Planning a whole book

```text
I want to write a Bengali horror novella (~30,000 words) set in an old zamindar house
in Natore. Help me plan it: book brief, story bible and chapter plan first, no prose yet.
```

For multi-chapter work, the skill keeps a project folder: a brief, a story bible, a chapter plan, a continuity ledger, one file per chapter, and editorial notes. It re-reads these before every chapter, so names, ages, clues and promises stay consistent across sessions. The templates are in `skills/book-writer/references/long-form-workflow.md`.

### Review and fact-check

```text
Review chapters 1-5 of my thriller as a developmental editor. Don't rewrite anything;
give me prioritized problems with locations and suggestions.
```

```text
এই ধর্মীয় বইয়ের অধ্যায়ে যত আয়াত আর হাদিস উদ্ধৃত হয়েছে, সেগুলোর রেফারেন্স যাচাই করো।
```

## Tips for the best results

- **Give the brief up front:** genre, readers, length, POV and tense, and ending type. Otherwise Claude makes reasonable choices and lists its assumptions in the reply.
- **For long projects, keep the project files in your working directory.** Approved briefs and bibles outrank the general rules (§2.3).
- **Say "edit in place"** if you want your file overwritten. By default, edits go to a new file.
- **To change house style** (for example, if you prefer করলো over করল), edit `references/bengali-craft.md` §1 and `VARIANT_PAIRS` in the checker.
