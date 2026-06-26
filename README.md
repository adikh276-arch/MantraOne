# MantraOne Backend
Longitudinal Family Health Memory System.

## Architecture 
4 layers: Watchers -> Coordinator -> Memory -> Escalation.

## Local Development Setup
- Preferred: Native Python (`uv`)
- Run `uv sync` to install dependencies.
- `ruff check .`, `mypy .`, `pytest` for validation.

## CI/CD 
- GitHub Actions is the source of truth for build health.
- Pushes to GHCR (`ghcr.io`).
- Triggers deployment orchestrator via webhook.
