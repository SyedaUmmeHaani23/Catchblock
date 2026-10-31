# CatchBlock

**Catch issues before they catch you.**

CatchBlock checks the health of a code repository. Paste a public GitHub link (or a local folder) and it gives you a 0 to 100 score, plain-English findings, a commit heartbeat and safe fixes. It only reads files: nothing from the scanned repo is ever executed.

## What it checks

| Check | What it looks for |
| --- | --- |
| LICENSE | A licence file exists and is a recognised open-source licence |
| README | Setup, usage and contributing sections |
| .gitignore | Present, so keys and build output are not committed |
| Secrets | Leaked keys and `.env` files in the current files |
| Secrets in history | Keys that were committed and later deleted but still sit in git history (values are never shown) |
| CI | A workflow (GitHub Actions, GitLab, CircleCI and others) |
| Tests | A test folder or test files |
| CONTRIBUTING | A guide for newcomers |
| AI tools and credits | AI tool files or packages detected but not named in the README, and a missing Credits section |
| Dependencies | Lockfile present and versions pinned |
| Git history | Commit count, contributors, giant dump commits, vague messages |
| Event rules (optional) | A rulebook file can add: licence in the first commit, event window, minimum contributors |

## What makes it different

- **Deleted-secret detection.** Most beginner tools only read the current files. CatchBlock also reads recent commits and warns when a secret was removed but is still readable in history.
- **Quick wins.** Findings are ranked by points gained, with a projected score if you apply the suggested fixes.
- **Safe fixes.** Every fix shows a diff first, never overwrites a file, and can be undone. GitHub repos stay read-only: you download a `.patch`.
- **Commit heartbeat.** A timeline of commits with review signals (before the event, after the freeze, giant dump). A signal is a reason to look closer, never proof.
- **Pre-push guard.** An optional git hook that blocks a push with a leaked secret or no licence.
- **Local explainer (optional).** "Explain it simply" asks a local Gemma model (through Ollama) to reword a finding. The scanner stays the source of truth and the score never depends on the model.

## Run it

You need Python 3.11+, Git and Node.js 20.19+ (or 22+).

Windows: double-click `start-windows.bat`. Or use two terminals:

```
cd cb
python -m catchblock.cli serve
```

```
cd web
npm install
npm run dev
```

Open http://localhost:5173 and paste a public GitHub repository link. Local folders work too.

Optional explainer: install [Ollama](https://ollama.com), then run `ollama pull gemma3:4b`. Without it everything else still works.

## Command line

```
python -m catchblock.cli scan https://github.com/owner/repo
python -m catchblock.cli scan C:\path\to\folder --json
python -m catchblock.cli scan . --rules devforge
python -m catchblock.cli guard install C:\path\to\your\repo
```

## Tests

```
cd cb
python -m unittest discover -s tests -v
```

## Safety

- Public `github.com` links only. The repo is cloned read-only, shallow, into a temporary folder with size and time limits, then deleted.
- No repository code, hook or install script is run.
- The local API only accepts requests from localhost.
- Error messages never include local paths.

## Honest limits

- A finding is a signal, not proof. A secret pattern can be a false alarm, and a commit pattern is not evidence of misconduct.
- The projected score is an estimate.
- Secrets in history look at the most recent 300 commits. Scans of GitHub links fetch up to 500 commits.
- It does not replace specialist tools such as OpenSSF Scorecard or a full secret scanner.

## Contribute

1. Fork the repo and create a branch.
2. Add a check in `cb/catchblock/checks/` (one function that returns a `Finding`), register it in `scanner.py`, and add a test in `cb/tests/`.
3. Event rulebooks live in `cb/rules/*.toml`. Copy one and change the dates and requirements.
4. Run the tests, then open a pull request.

Good first issues: a SECURITY.md check, issue and PR template checks, more secret patterns.

## AI tools used

- **Claude (Anthropic)** was used as a coding assistant while building this project. Every team member can explain the code.
- **Gemma 3 via Ollama** is an optional local model for plain-English explanations. It runs on your own machine.

## Credits

- [React](https://react.dev) and [Vite](https://vite.dev) for the web app (MIT)
- Fonts from Google Fonts: Sora, Inter, JetBrains Mono (SIL Open Font License)
- Python standard library and [Git](https://git-scm.com)
- [Ollama](https://ollama.com) and Google's Gemma (optional explainer)
- Add here any template, snippet or library you copied from another project, with its author and licence.

## License

See the LICENSE file in this repository.

## More features
- **Score trend.** Scan again after fixing and the report shows the change since last time. History stays on your computer (`~/.catchblock/history.json`).
- **Health badge.** Download a self-contained SVG for your README from the report, or run `python -m catchblock.cli scan . --badge catchblock-badge.svg`.
- **Issue checklist.** Copy every open finding as a Markdown to-do list for a GitHub issue or pull request (`--markdown` on the CLI).
- **CI gate.** `python -m catchblock.cli scan . --min-score 70` exits with code 1 when the score is lower, so a pipeline can fail the build.
- **Optional rulebooks.** `cb/rules/*.toml` can add an event window, minimum contributors or a licence from the first commit. The website uses `cb/rules/default.toml`, which has no event.

