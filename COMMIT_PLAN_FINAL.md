Suggested commits for the merge (use your own real times and messages):
1. feat: scan public GitHub URLs via a safe temporary read-only clone      -> cb/catchblock/gitsource.py, server.py
2. feat: rulebook loader and event rules                                    -> cb/catchblock/rules.py, cb/rules/
3. feat: AI-tool, credits and dependency checks                             -> cb/catchblock/checks/ai.py, deps.py
4. feat: detect secrets deleted from git history                            -> cb/catchblock/checks/security.py
5. feat: quick wins with a projected score                                  -> cb/catchblock/scanner.py
6. feat: optional local Gemma explainer                                     -> cb/catchblock/explain.py, server.py
7. fix: generic-repo defaults (licence list, solo repos, test detection)    -> cb/catchblock/checks/
8. chore: remove judge estimate, new tagline                                -> web/src, cb/
9. feat(web): quick wins section and Explain it simply                      -> web/src/report/
10. docs: README, run guide, credits
