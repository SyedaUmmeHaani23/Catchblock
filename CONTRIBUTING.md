# Contributing to CatchBlock

1. Fork the repository and create a feature branch:
   `git checkout -b feat/my-change`.
2. Backend: run `cd cb` and `python -m unittest discover -s tests -v`.
3. Frontend: run `cd web`, `npm install`, and `npm run build`.
4. Make small commits with clear messages, such as `fix: handle empty README`.
5. Open a pull request explaining what changed and why.

New checks live in `cb/catchblock/checks/`.
Add a test for each new check in `cb/tests/`.
