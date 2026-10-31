# How to run CatchBlock

1. Terminal 1:  `cd cb` then `python -m catchblock.cli serve`   (API on http://localhost:8000)
2. Terminal 2:  `cd web` then `npm install` then `npm run dev`   (site on http://localhost:5173)
3. Open http://localhost:5173, paste a public GitHub link, press Scan.

Windows shortcut: double-click `start-windows.bat`. Mac/Linux: `./start.sh`.

Needs: Python 3.11+, Git, Node 20.19+ (or 22+), and internet for GitHub scans.
Optional: `ollama pull gemma3:4b` for the "Explain it simply" button.

## Before the demo
- Run `npm run build` in `web/` once to make sure it builds.
- Run the tests: `cd cb` then `python -m unittest discover -s tests -v` (45 should pass).
- Scan one healthy repo and one messy repo so you know what the audience will see.
- `cb/rules/devforge.toml` has the Devf8rge window (30 Oct 10 PM to 31 Oct 10 AM IST). Check it against the rulebook.
- GitHub URL scanning needs internet. It was tested here with local git remotes, not live GitHub.
