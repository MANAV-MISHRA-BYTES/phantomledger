"""Read-only Git extraction. Every invocation is an explicitly defined command."""
import os
import subprocess
from pathlib import Path


class GitError(ValueError):
    pass


def validate_repo(raw_path: str) -> Path:
    path = Path(raw_path).expanduser().resolve(strict=True)
    if not path.is_dir() or not (path / ".git").exists():
        raise GitError("Choose a directory containing a valid .git directory.")
    return path


def git(repo: Path, *args: str, check: bool = True) -> str:
    env = {**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_PAGER": "cat", "GIT_CONFIG_NOSYSTEM": "1"}
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=30, env=env)
    if check and result.returncode:
        raise GitError(result.stderr.strip() or "Git could not read this repository.")
    return result.stdout


def inspect_repository(raw_path: str) -> dict:
    repo = validate_repo(raw_path)
    commits_raw = git(repo, "log", "--all", "--date=iso-strict", "--format=%H%x1f%h%x1f%ad%x1f%an%x1f%s", "--name-status", "-n", "500")
    commits = []
    current = None
    for line in commits_raw.splitlines():
        if "\x1f" in line:
            bits = line.split("\x1f", 4)
            current = {"sha": bits[0], "short_sha": bits[1], "date": bits[2], "author": bits[3], "message": bits[4], "files": [], "changes": []}
            commits.append(current)
        elif line and current:
            cols = line.split("\t")
            if len(cols) >= 2:
                status, file = cols[0], cols[-1]
                current["files"].append(file)
                current["changes"].append({"status": status, "file": file})
    branch_lines = git(repo, "for-each-ref", "--format=%(refname:short)%09%(objectname:short)%09%(committerdate:iso-strict)%09%(HEAD)", "refs/heads", "refs/remotes").splitlines()
    branches = []
    for line in branch_lines:
        p = line.split("\t")
        if p and p[0]: branches.append({"name": p[0], "sha": p[1] if len(p)>1 else "", "date": p[2] if len(p)>2 else "", "current": len(p)>3 and p[3]=="*"})
    current_branch = git(repo, "branch", "--show-current", check=False).strip()
    head_files = set(git(repo, "ls-files").splitlines())
    return {"path": str(repo), "commits": commits, "branches": branches, "current_branch": current_branch,
            "head_files": sorted(head_files), "stats": {"commits": len(commits), "branches": len(branches) or 1,
            "contributors": len({c['author'] for c in commits}), "files": len(head_files)}}

