# CatchBlock Architecture

## Overview
CatchBlock is a repository health and hackathon-readiness scanner.

## Main components

### Backend
Located in `cb/catchblock/`.

- scanner.py: Coordinates repository scanning.
- score.py: Calculates repository health scores.
- rules.py: Loads scanning rules.
- gitsource.py: Handles temporary GitHub repository checkouts.
- fixes.py: Provides safe fix operations.
- server.py: Exposes the API.

### Frontend
Located in `web/src/`.

- pages/: Landing page and dashboard.
- components/: Reusable interface components.
- report/: Scan results and findings.
- lib/: API and utility functions.

## Data flow

1. User submits a local repository or GitHub URL.
2. Backend inspects repository files and Git history.
3. Checks generate findings.
4. Scoring logic calculates the repository score.
5. Frontend displays findings and recommended improvements.

## Safety
Remote repository code is inspected, not executed.
Temporary checkouts are cleaned up after scanning.
