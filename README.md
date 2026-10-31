# PhantomLedger 👻

**Your repository remembers what you forgot.**

PhantomLedger is a local-first developer archaeology tool that reconstructs a repository’s memory from Git history, then lets a local Gemma model interpret a selected evidence bundle.

## What It Is

A Memory Ledger for the decisions, experiments, branches, files, and notes that shaped a codebase. The interface keeps verified Git facts visually separate from model interpretation.

## The Problem

The working tree only shows what survived. Reverted work, deleted modules, abandoned branches, repeated edits, and unresolved TODOs can hold useful context that is easy to lose.

## How It Works

1. Choose a repository or create the built-in synthetic demo.
2. PhantomLedger runs fixed, read-only Git commands and extracts commits, branches, file changes, authors, and dates.
3. Deterministic Python rules score and summarize historical memories.
4. Ask Gemma to interpret one selected memory. Only that memory’s evidence is sent to Ollama.
5. Review facts and AI interpretation in separate sections. If Ollama is unavailable, the evidence remains usable without a fabricated answer.

**Git provides deterministic historical evidence. Gemma provides local interpretation.** The model does not calculate dates or commit relationships.

## Architecture

- **Backend:** Python 3.10+, FastAPI, Pydantic
- **Frontend:** Vanilla HTML, CSS, and JavaScript
- **Git:** Native Git CLI through explicit subprocess commands
- **AI:** Local Ollama API with configurable Gemma model
- **Storage:** In-memory analysis cache; the analyzed repository is not modified

## Memory Types

Deleted files, explicitly reverted changes, abandoned branches, long-lived TODO/FIXME markers, repeatedly modified files, short-lived experiments, and contributor inactivity. Each memory includes a stable ID, interest score, dates, commits, files, authors, evidence, and a deterministic summary.

## Why Gemma

Gemma can turn a narrow evidence bundle into a concise historical explanation while running locally. The prompt asks for known facts, unknowns, interpretation, and confidence as structured JSON; Pydantic validates the result. The application never treats generated prose as Git evidence.

## Why Open Innovation Matters

Open-weight AI lets developers inspect, run, and control the model locally. For code archaeology, that means private repository data can stay on the developer’s machine, the tool can work without a cloud AI account, and users can choose their model. This project sends no repository content to a cloud AI provider.

## Safety

- Analysis only accepts a directory containing `.git`.
- Git invocations are fixed by the application; no model output becomes a command.
- The analyzer does not checkout branches, write into the inspected repository, commit, push, pull, or delete user files.
- Ollama is contacted only after the user asks for interpretation, and only with the selected memory evidence.
- The demo generator writes only to a dedicated temporary demo directory.

## Installation

Requirements: Python 3.10+, Git, and (optionally) Ollama with a Gemma model available.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

Optional local AI setup:

```powershell
ollama pull gemma4:e4b
```

## Running Locally

```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Open <http://127.0.0.1:8000>. Configure the model with `PHANTOMLEDGER_MODEL=gemma4:e4b` and the local Ollama endpoint with `PHANTOMLEDGER_OLLAMA_URL=http://localhost:11434`. For safety, only `localhost`, `127.0.0.1`, or `::1` endpoints are accepted; remote Ollama-compatible URLs are rejected.

## Creating the Demo Repository

Click **Create Haunted Demo Repository**. PhantomLedger programmatically creates a synthetic Git repository with a legacy auth module, a SQLite experiment on an unmerged branch, a dashboard commit and explicit revert, a JWT transition, repeated app edits, an abandoned dashboard branch, and a TODO that persists across commits. No remote repository is downloaded.

## Example

Select the **Reverted** filter and open the dashboard memory. Git records the prototype commit and its later revert. Gemma can summarize those facts, but when the record provides no motive, the model should say that the reason is unknown.

## Testing

```powershell
pytest -q
```

Tests create temporary repositories and do not require Ollama.

## Project Structure

```text
backend/        FastAPI API, Git analysis, memories, Gemma client, demo generator
frontend/       Single-page local interface
demo/           Synthetic demo repository notes
docs/           Recording script
tests/          Git, memory, and API tests
```

## Limitations

History is capped at 500 commits for analysis. Branch reachability and TODO persistence are heuristics, and repository-specific workflows may need more context than commit metadata can provide. Local Gemma quality and speed depend on the selected model and machine. The chronicle only summarizes detected deterministic milestones.

## Future Improvements

Broader rename detection, richer diff statistics, configurable analysis depth, and memory export formats.

## License

MIT.
