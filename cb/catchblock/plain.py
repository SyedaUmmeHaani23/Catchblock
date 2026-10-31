"""Built-in plain-English guidance for every finding. No AI, no API key, works offline."""

PLAIN = {
    "license.exists": ("A licence is a short file that says what other people may do with your code. Without one, the default is that nobody may copy or reuse it.",
                       "Add a LICENSE file. MIT is a simple, popular choice. Use Apply fix to create it."),
    "license.type": ("Your licence file was not recognised as a common open-source licence.",
                     "Replace it with the official text of MIT, Apache-2.0 or another standard licence (choosealicense.com lists them)."),
    "license.first_commit": ("The licence was added after the project had already started.",
                             "History cannot be undone. Keep the licence in every commit from now on."),
    "docs.readme": ("The README is the front page of your project. People decide within seconds whether to use it.",
                    "Say what the project does, how to install it, how to use it and how to contribute."),
    "hygiene.gitignore": ("A .gitignore file tells git which files to leave out, such as secrets, installed packages and build folders.",
                          "Add a .gitignore for your language so private or generated files are never committed."),
    "secrets.scan": ("A password, key or token was found in your files. Anyone who can see the repository can use it.",
                     "Treat it as stolen: create a new key in the service's dashboard, remove the old one from the code and load keys from environment variables."),
    "secrets.history": ("A secret was committed in the past and deleted later, but git remembers every old version, so it can still be read.",
                        "Revoke and replace that secret first. Cleaning history rewrites the project's past, so agree it with your team."),
    "ci.workflow": ("Continuous integration runs your tests automatically on every push, so broken code is caught early.",
                    "Add a workflow file in .github/workflows that installs the project and runs the tests."),
    "tests.exist": ("No tests were found, so nothing proves the code still works after a change.",
                    "Start small: write one test for the most important function and run it before every push."),
    "community.contributing": ("A CONTRIBUTING file tells newcomers how to help: how to set up and how to submit changes.",
                               "Add a short CONTRIBUTING.md with setup steps and how to open a pull request."),
    "disclosure.ai": ("AI tools were used or detected, but the README does not say so. Being open about it builds trust.",
                      "Add an 'AI tools used' list that names each tool and what it helped with."),
    "credits.readme": ("The project builds on other people's libraries, but the README does not thank them.",
                       "Add a Credits section listing the main libraries, templates and any borrowed code."),
    "deps.hygiene": ("Your list of libraries can install different versions on different computers, which makes bugs hard to reproduce.",
                     "Commit a lock file and avoid '*', 'latest' or unpinned versions."),
    "git.history": ("Very few commits usually means work was saved in big chunks.",
                    "Commit small, finished steps with clear messages."),
    "git.authors": ("Only one person has committed. Projects with several contributors are easier to keep alive.",
                    "If this is a team project, make sure everyone commits their own work."),
    "git.dump": ("One commit holds most of the code. That hides how the project grew and makes mistakes hard to trace.",
                 "From now on, commit in small steps."),
    "git.messages": ("Many commit messages are vague words like 'fix' or 'update'.",
                     "Say what changed and why, for example 'fix: handle empty input in the parser'."),
    "git.repo": ("No git history was found, so the report cannot show how the project was built.",
                 "Run git init and make a first commit, or scan a full clone."),
    "git.window": ("Some commits are dated outside the window set by the selected rules.",
                   "This is a signal for review. Check the dates and be ready to explain them."),
}
FALLBACK = ("This check looks for something that usually makes a project harder to trust, run or maintain.",
            "Read 'Why it matters', then use the suggested fix if there is one.")

def plain_for(finding_id: str) -> dict:
    mean, step = PLAIN.get(finding_id, FALLBACK)
    return {"mean": mean, "step": step}
