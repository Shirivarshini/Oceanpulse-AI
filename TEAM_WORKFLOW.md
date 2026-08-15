# OceanPulse AI Team Workflow

## Ownership

- Member 1 → frontend/
- Member 2 → backend/
- Member 3 → ml/
- Member 4 → data-pipeline/

## Branches

- frontend
- backend
- fusion-engine
- data-edna

## Integration

The main branch is the shared integration branch.

The integration flow is:

data-pipeline
→ Fusion Engine
→ FastAPI
→ Alert Gate
→ frontend

Each member must work on their assigned branch and submit a Pull Request to main.

## Workflow guidance

- Each member creates and works on their named branch.
- Changes are opened as a Pull Request to the main branch for review and integration.
- Keep the main branch as the canonical integration environment. Use feature branches for work-in-progress.
