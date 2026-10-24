# Installation

The skill is a plain folder, `skills/book-writer/`, in the open [Agent Skills](https://agentskills.io) format: a `SKILL.md` with `name` and `description` front matter, plus `references/` and `scripts/`. Any tool that supports Agent Skills can load it.

| Platform | Method | Jump to |
|---|---|---|
| Claude Code | Plugin marketplace (recommended) or copy the folder | [Claude Code](#claude-code) |
| Claude.ai (web and desktop apps) | Upload a ZIP | [Claude.ai](#claudeai) |
| Claude API | Skills API + code execution tool | [Claude API](#claude-api) |
| Claude Agent SDK | `.claude/skills/` + `setting_sources` | [Agent SDK](#claude-agent-sdk) |
| Codex, Copilot CLI, Cursor, OpenCode, Gemini CLI | Copy into the tool's skills directory | [Other agents](#other-ai-coding-agents) |
| Chat assistants without skill support | Instructions + knowledge files | [Other assistants](#chat-assistants-without-skill-support) |

**Requirement for the manuscript checker:** Python 3.8+ (standard library only). Without Python, the skill still works, but Claude checks the same rules by eye.

---

## Claude Code

### Option A: Plugin marketplace (recommended)

Run inside Claude Code:

```text
/plugin marketplace add akr4m/book-writer-skills
/plugin install book-writer@book-writer-skills
```

Or from your shell:

```bash
claude plugin marketplace add akr4m/book-writer-skills
claude plugin install book-writer@book-writer-skills
```

Plugin skills are namespaced, so the explicit command is `/book-writer:book-writer`. You rarely need it, because the skill triggers on its own for book-writing requests.

To pick up new versions later:

```bash
claude plugin marketplace update book-writer-skills
```

### Option B: Personal install (all your projects)

```bash
git clone https://github.com/akr4m/book-writer-skills.git
mkdir -p ~/.claude/skills
cp -R book-writer-skills/skills/book-writer ~/.claude/skills/
```

To get updates with a simple `git pull`, link the folder instead of copying it:

```bash
ln -s "$(pwd)/book-writer-skills/skills/book-writer" ~/.claude/skills/book-writer
```

Windows (PowerShell):

```powershell
git clone https://github.com/akr4m/book-writer-skills.git
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse book-writer-skills\skills\book-writer "$HOME\.claude\skills\"
```

### Option C: Project install (one project, shared with your team through git)

```bash
mkdir -p .claude/skills
cp -R /path/to/book-writer-skills/skills/book-writer .claude/skills/
```

### Check that it loaded

Claude Code watches the skills directories, so a restart is usually unnecessary. If you created a new top-level `skills/` directory during a session, run `/reload-skills`. Then:

```text
/book-writer একটা ছোট্ট ভূতের গল্পের তিনটা ভিন্ন premise দাও
```

(For a marketplace install, use `/book-writer:book-writer`.)

---

## Claude.ai

This works in the web app and the desktop apps, on Free, Pro, Max, Team and Enterprise plans. On Team and Enterprise, an owner may have turned skill creation off.

1. **Turn on code execution.** Go to **Settings → Capabilities** and enable **Code execution and file creation**. Skills need it.
2. **Build the ZIP.** The folder name must match the skill name (`book-writer`), with `SKILL.md` directly inside it.

   ```bash
   git clone https://github.com/akr4m/book-writer-skills.git
   cd book-writer-skills/skills
   zip -r book-writer.zip book-writer -x "book-writer/evals/*" "*/__pycache__/*"
   ```

   On Windows, right-click the `book-writer` folder and choose **Send to → Compressed (zipped) folder**.
3. **Upload it.** Open **Customize → Skills** (claude.ai/customize/skills), click **+ → Create skill → Upload a skill**, and choose `book-writer.zip`.
4. **Use it.** Start a new chat and ask for book work, for example "এই অধ্যায়টা প্রুফ দেখো". Claude loads the skill when the request matches.

Menu names on claude.ai change from time to time. If a label differs, look for **Skills** under Customize or Settings.

---

## Claude API

Upload the skill once. You get back a `skill_id` scoped to your workspace, which you then attach to Messages requests along with the code execution tool.

```python
import anthropic
from anthropic.lib import files_from_dir

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY

# 1. Upload once (the directory must contain SKILL.md at its root) and store skill.id
skill = client.skills.create(files=files_from_dir("book-writer-skills/skills/book-writer"))
print(skill.id)

# 2. Use it in a request
response = client.messages.create(
    model="claude-opus-5-5",  # any model that supports the code execution tool
    max_tokens=16000,
    container={"skills": [{"type": "custom", "skill_id": skill.id, "version": "latest"}]},
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
    messages=[{
        "role": "user",
        "content": "সিলেটের চা-বাগানে বর্ষার রাতে একটা ১৫০০ শব্দের রহস্য গল্প লেখো।",
    }],
)
print(response.content)
```

Notes:
- Upload uses `POST /v1/skills` (multipart). Up to 20 skills can be attached to one request.
- Older SDK versions sent beta headers for skills and code execution. If your SDK raises a beta-related error, upgrade the `anthropic` package.
- Reference: [Using Agent Skills with the API](https://platform.claude.com/docs/en/build-with-claude/skills-guide).

---

## Claude Agent SDK

The SDK loads skills only from `.claude/skills/`, either in your project or in your user directory. Copy the folder there first:

```bash
mkdir -p .claude/skills
cp -R book-writer-skills/skills/book-writer .claude/skills/
```

```python
from claude_agent_sdk import query, ClaudeAgentOptions

options = ClaudeAgentOptions(
    cwd="/path/to/your/book-project",
    setting_sources=["user", "project"],  # where skills are loaded from
    skills=["book-writer"],               # or "all"
)

async for message in query(prompt="Proofread manuscript/03-chapter.md", options=options):
    print(message)
```

Passing `skills` adds the `Skill` tool automatically. If you pass an explicit `tools` list, include `"Skill"` in it. Reference: [Agent SDK skills](https://code.claude.com/docs/en/agent-sdk/skills).

---

## Other AI coding agents

These tools read the same `SKILL.md` format. Copy `skills/book-writer` into the directory your tool scans:

| Tool | Project directory | Personal directory |
|---|---|---|
| OpenAI Codex | `.agents/skills/` | `~/.agents/skills/` |
| GitHub Copilot CLI | `.github/skills/`, `.agents/skills/`, `.claude/skills/` | `~/.copilot/skills/`, `~/.agents/skills/` |
| Cursor | `.cursor/skills/`, `.agents/skills/` | `~/.cursor/skills/`, `~/.agents/skills/` |
| OpenCode | `.opencode/skills/`, `.agents/skills/`, `.claude/skills/` | `~/.config/opencode/skills/`, `~/.agents/skills/` |
| Gemini CLI* | `.gemini/skills/`, `.agents/skills/` | `~/.gemini/skills/`, `~/.agents/skills/` |

\* Google has announced that Antigravity CLI replaces Gemini CLI, so check its current docs.

`~/.agents/skills/` is the shared location most of these tools read:

```bash
mkdir -p ~/.agents/skills
cp -R book-writer-skills/skills/book-writer ~/.agents/skills/
```

The skill was written and tested with Claude. Other models can follow it, but expect more variation, especially in Bengali prose quality. The checker needs the agent to be able to run `python3`.

---

## Chat assistants without skill support

For assistants that only support custom instructions and uploaded files (custom GPTs, Gems, project knowledge bases, and similar):

1. Paste the body of `SKILL.md` (everything after the front matter) into the assistant's **instructions**.
2. Upload the files in `references/` (including `references/standard/`) as **knowledge files**.
3. If the assistant can run Python, upload `scripts/check_manuscript.py` too, and ask it to run the script on its drafts.

This is an approximation. Without progressive loading, the assistant sees every rule at once, and paths such as `references/standard/03-fiction.md` refer to uploaded file names rather than folders.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| The skill doesn't trigger | Name it: "Use the book-writer skill to …", or `/book-writer` (`/book-writer:book-writer` for plugin installs). |
| `python3: command not found` | Install Python 3, or ignore it: the skill falls back to manual checks. |
| Bengali text looks broken in the terminal | That's a terminal font issue. Open the `.md` file in an editor with a Bengali font (e.g. Noto Sans Bengali). |
| Claude.ai upload rejected | Make sure the ZIP contains `book-writer/SKILL.md`, not `SKILL.md` at the root of a differently named folder. |
| Changes to the rules don't show up | For plugin installs, update the marketplace. For copies, re-copy the folder, or use a symlink. |
