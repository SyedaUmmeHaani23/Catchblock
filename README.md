# 🛡️ CatchBlock

### Catch issues before they catch you.

**A repository health and readiness analyzer that helps developers identify problems before sharing, submitting, or shipping their code.**

<p align="center">
  <a href="https://catchblock.vercel.app">🌐 Live Application</a> •
  <a href="https://catchblock.onrender.com">⚙️ Backend API</a> •
  <a href="https://github.com/SyedaUmmeHaani23/Catchblock">💻 GitHub Repository</a>
</p>

---

## 🚨 The Problem

Building a project is more than writing code.

A repository may work perfectly on a developer's machine and still be far from ready to share or submit.

A missing README, exposed credentials, unpinned dependencies, absent tests, incomplete documentation, or suspicious Git history can make an otherwise promising project difficult to maintain, review, or trust.

For beginners, identifying these problems is even harder. Many tools report technical issues without explaining what they mean or what to do next.

**Developers need more than another error message. They need to understand the health of their repository and know how to improve it.**

## 💡 Our Solution: CatchBlock

CatchBlock brings repository health checks into one place.

Provide a public GitHub repository URL or scan a local folder, and CatchBlock analyzes the repository, generates a health score from 0–100, identifies potential issues, explains findings in plain English, and suggests actionable improvements.

It also provides commit-history insights, safe fix previews, reports, health badges, and developer workflow integrations.

Our objective is to make repository quality, security, and readiness easier to understand and improve — especially for student developers, hackathon participants, and open-source contributors.

---

## 🌐 Try CatchBlock

| Component | Link |
|---|---|
| Live Frontend | https://catchblock.vercel.app |
| Backend API | https://catchblock.onrender.com |
| Backend Health Check | https://catchblock.onrender.com/health |
| Source Code | https://github.com/SyedaUmmeHaani23/Catchblock |

**How to try it:**
1. Open the live application.
2. Enter a public GitHub repository URL.
3. Start the scan.
4. Review the repository health score and findings.
5. Explore explanations and suggested improvements.

> Note: The free backend hosted on Render may take some time to wake up after inactivity. The first scan may therefore take longer.

---

## ✨ Key Features

### 1. Repository Health Score
- Generates an overall repository health score from 0–100.
- Identifies potential quality, security, documentation, and readiness issues.
- Helps developers understand areas that need attention.

### 2. Comprehensive Repository Checks

| Check | What it looks for |
|---|---|
| LICENSE | Licence file existence and recognised open-source licences |
| README | Setup, usage, and contributing sections |
| .gitignore | Presence of files that help prevent committing keys and build output |
| Secrets | Potential leaked keys and `.env` files in current files |
| Secrets in history | Secrets committed and later deleted but still present in Git history; values are never displayed |
| CI | Workflows such as GitHub Actions, GitLab CI, and CircleCI |
| Tests | Test folders and test files |
| CONTRIBUTING | Contributor documentation |
| AI tools and credits | AI-related files or packages not acknowledged in the README, and missing Credits sections |
| Dependencies | Lockfiles and pinned dependency versions |
| Git history | Commit count, contributors, unusually large commits, and vague messages |
| Event rules | Optional rulebooks for event windows, minimum contributors, and licence requirements |

### 3. Plain-English Explanations
Technical findings can be difficult to understand, particularly for beginners.

CatchBlock helps explain findings in simple language so developers can understand:
- What the issue is.
- Why it matters.
- What they can do about it.

### 4. Deleted-Secret Detection
CatchBlock goes beyond checking the current files.

It also examines recent Git history to identify potential secrets that were committed and subsequently deleted but may remain accessible in previous commits.

Secret values are never displayed in findings.

### 5. Smart Quick Wins
- Ranks findings by potential points gained.
- Highlights improvements that can make the biggest difference.
- Provides a projected score after suggested fixes.

The projected score is an estimate, not a guaranteed result.

### 6. Safe Fixes and Undo
- Previews proposed changes through diffs.
- Avoids silently overwriting existing files.
- Supports undo for applicable local changes.
- For GitHub repositories, fixes remain read-only and can be downloaded as `.patch` files.

### 7. Commit Heartbeat
A timeline of repository commits with review signals such as:
- Activity before an event.
- Activity after a freeze.
- Unusually large commits.
- Vague commit messages.

These signals help reviewers investigate patterns. They are not proof of misconduct.

### 8. Pre-push Guard
An optional Git hook that can block a push when it detects a leaked secret or a missing licence.

### 9. Reports, Badges and Score History
- Generates Markdown reports.
- Provides an issue checklist for GitHub issues and pull requests.
- Generates a downloadable SVG health badge.
- Tracks score changes across scans.
- Keeps local score history on the user's computer.

### 10. CI Score Gate
Use the CLI minimum-score option to make a CI pipeline fail when a repository falls below a chosen health score.

### 11. Optional Local AI Explainer
CatchBlock supports an optional local Gemma model through Ollama.

It can reword findings into simpler explanations. The scanner remains the source of truth: AI does not determine the repository score or verdict.

---

## 🏗️ How It Works

```text
        Developer
            |
            v
   Public GitHub URL
      or Local Folder
            |
            v
    CatchBlock Frontend
       React + Vite
            |
            v
      Python Backend
            |
            v
    Repository Analysis
            |
     +------+------+
     |      |      |
     v      v      v
  Security Quality Git History
  Checks   Checks  Analysis
     |      |      |
     +------+------+
            |
            v
     Health Score
     Findings
     Explanations
     Suggested Fixes
            |
            v
      Actionable Report
```

### Architecture

| Layer | Technology | Responsibility |
|---|---|---|
| Frontend | React.js | User interface and scan experience |
| Build tool | Vite | Frontend development and production build |
| Backend | Python | API and repository analysis |
| Version control | Git | Repository and commit-history analysis |
| Rule engine | TOML rulebooks | Configurable repository checks |
| Optional AI | Ollama + Gemma 3 | Local plain-English explanations |
| Frontend hosting | Vercel | Live web application |
| Backend hosting | Render | Hosted API service |
| CI/CD | GitHub Actions | Automated backend tests and frontend build |

---

## 🔐 Safety and Trust

Safety is an important part of CatchBlock's design.

- Public GitHub repository URLs are supported for remote scanning.
- Repository cloning is read-only and uses temporary storage, size limits, and time limits.
- Repository code, hooks, and installation scripts are not executed during scanning.
- Deleted-secret detection does not expose secret values.
- Error messages avoid exposing local filesystem paths.
- Fixes are previewed before application.
- GitHub repository scans remain read-only; suggested changes can be downloaded as patches.

**Important deployment distinction:**
The hosted application scans public GitHub repositories through its remote backend. Local-folder scanning and local filesystem fix operations require the locally running application and backend. A hosted server cannot directly access folders on a visitor's computer.

---

## 🚀 Run CatchBlock Locally

### Prerequisites

- Python 3.11+
- Git
- Node.js 20.19+ or 22+

### 1. Clone the repository

```bash
git clone https://github.com/SyedaUmmeHaani23/Catchblock.git
cd Catchblock
```

### 2. Start the backend

Open a terminal:

```bash
cd cb
python -m catchblock.cli serve
```

The backend runs locally at:

```text
http://localhost:8000
```

### 3. Start the frontend

Open another terminal:

```bash
cd web
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

You can now scan public GitHub repositories and supported local folders.

### Windows shortcut

You can also use:

```text
start-windows.bat
```

### Optional: Enable the local AI explainer

Install [Ollama](https://ollama.com), then run:

```bash
ollama pull gemma3:4b
```

The rest of CatchBlock works without Ollama.

---

## ⌨️ Command-Line Usage

Scan a public GitHub repository:

```bash
python -m catchblock.cli scan https://github.com/owner/repo
```

Scan a local folder:

```bash
python -m catchblock.cli scan C:\path\to\folder --json
```

Scan with an event rulebook:

```bash
python -m catchblock.cli scan . --rules devforge
```

Install the pre-push guard:

```bash
python -m catchblock.cli guard install C:\path\to\your\repo
```

Generate a health badge:

```bash
python -m catchblock.cli scan . --badge catchblock-badge.svg
```

Apply a minimum score requirement:

```bash
python -m catchblock.cli scan . --min-score 70
```

---

## 🧪 Testing

CatchBlock includes automated backend tests and a frontend production build.

### Backend tests

```bash
cd cb
python -m unittest discover -s tests -v
```

**Latest local backend test result:** 57 tests passed.

### Frontend production build

```bash
cd web
npm install
npm run build
```

**Latest verified build:** Vite production build completed successfully.

### GitHub Actions

The repository includes a GitHub Actions workflow that runs:
- Backend automated tests.
- Frontend dependency installation.
- Frontend production build.

The latest verified CI run completed successfully for both jobs.

---

## ☁️ Deployment

CatchBlock uses separate hosting for its frontend and backend.

| Service | Platform | Deployment |
|---|---|---|
| Frontend | Vercel | https://catchblock.vercel.app |
| Backend | Render | https://catchblock.onrender.com |

The frontend communicates with the backend through the configured API endpoint.

The frontend uses the `VITE_API` environment variable to identify the backend API URL.

For the deployed application, the backend must be configured to allow the deployed frontend origin.

**Hosting note:** Free Render instances can spin down after inactivity, resulting in a delay on the first request. Local history and filesystem-based features should not be assumed to persist on a hosted instance.

---

## ⚖️ Honest Limitations

CatchBlock is designed as a repository-readiness assistant, not a replacement for a complete security audit.

- A finding is a signal, not proof. Secret patterns can produce false positives.
- Commit patterns do not establish intent or misconduct.
- Projected scores are estimates.
- Secret-history checks examine the most recent 300 commits.
- GitHub URL scans fetch up to 500 commits.
- It does not replace specialist tools such as [OpenSSF Scorecard](https://scorecard.dev/) or a dedicated secret scanner.
- Hosted scanning is intended for public GitHub repositories; local folder scanning requires a local setup.
- The hosted service's free-tier availability and storage limitations may affect response time and persistence.

---

## 🤝 Contributing

Contributions and suggestions are welcome!

1. Fork the repository.
2. Create a feature branch.
3. Add a check in `cb/catchblock/checks/`.
4. Register the check in `scanner.py`.
5. Add an appropriate test in `cb/tests/`.
6. Run the tests.
7. Open a pull request.

Event rulebooks are available in:

```text
cb/rules/*.toml
```

### Good first issues
- Add a `SECURITY.md` check.
- Add issue and pull request template checks.
- Expand supported secret patterns.
- Improve repository-readiness rules.

---

## 🤖 AI Tools Used

- **Claude (Anthropic):** Used as a coding assistant during development. Every team member should be able to explain the code and implementation.
- **Gemma 3 via Ollama:** Optional local model used for plain-English explanations. It runs on the user's own machine.

---

## 🙌 Credits

- [React](https://react.dev) and [Vite](https://vite.dev) — frontend.
- Google Fonts — Sora, Inter, and JetBrains Mono.
- Python standard library and [Git](https://git-scm.com).
- [Ollama](https://ollama.com) and Google's Gemma — optional local explainer.

Add attribution and licence details for any additional templates, snippets, or libraries incorporated into the project.

---

## 📄 License

See the [LICENSE](LICENSE) file in this repository.

---

## 💚 Our Vision

We believe repository quality should not be something developers discover only after a failed submission, a difficult review, or a security incident.

Developers should be able to identify issues early, understand them clearly, and improve their projects with confidence.

**CatchBlock makes repository health easier to see, understand, and improve.**

### Catch issues before they catch you. 🛡️
