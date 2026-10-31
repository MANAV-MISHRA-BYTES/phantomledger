"""Create a deterministic, entirely local Git history for product demonstrations."""
import os, subprocess, tempfile
from pathlib import Path

def create_demo(base: str | None = None) -> str:
    root=Path(base) if base else Path(tempfile.mkdtemp(prefix="phantomledger-haunted-demo-"))
    if base:
        if root.exists() and any(root.iterdir()):
            raise FileExistsError("The chosen demo directory already contains files.")
        root.mkdir(parents=True, exist_ok=True)
    def git(*args):
        subprocess.run(["git","-C",str(root),*args],check=True,capture_output=True,text=True)
    def commit(msg,day):
        env={**os.environ,"GIT_AUTHOR_NAME":"Mara Chen","GIT_AUTHOR_EMAIL":"mara@example.test","GIT_COMMITTER_NAME":"Mara Chen","GIT_COMMITTER_EMAIL":"mara@example.test","GIT_AUTHOR_DATE":f"2026-10-{day:02}T12:00:00+00:00","GIT_COMMITTER_DATE":f"2026-10-{day:02}T12:00:00+00:00"}
        subprocess.run(["git","-C",str(root),"add","-A"],check=True,env=env,capture_output=True)
        subprocess.run(["git","-C",str(root),"commit","-m",msg],check=True,env=env,capture_output=True)
    git("init","-b","main"); git("config","user.name","Mara Chen"); git("config","user.email","mara@example.test")
    def write(name,content):
        p=root/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(content,encoding="utf-8")
    write("README.md","# Lantern\nA tiny service with a long memory.\n"); write("app.py","from auth.session import SessionAuth\n\ndef app():\n    return 'lantern'\n"); write("auth/session.py","class SessionAuth:\n    pass\n")
    commit("Initial project",1)
    write("auth/legacy.py","class LegacyAuth:\n    # Original session bridge\n    pass\n"); commit("Add legacy authentication",2)
    git("switch","-c","experiment/cache-layer"); write("cache/sqlite_cache.py","# SQLite cache experiment\nclass Cache:\n    pass\n"); commit("Experiment with SQLite caching",3)
    git("switch","main"); write("frontend/dashboard.html","<main>Lantern dashboard prototype</main>\n"); write("frontend/dashboard.js","document.body.dataset.view = 'prototype';\n"); commit("Add dashboard prototype",4)
    env={**os.environ,"GIT_AUTHOR_NAME":"Mara Chen","GIT_AUTHOR_EMAIL":"mara@example.test","GIT_COMMITTER_NAME":"Mara Chen","GIT_COMMITTER_EMAIL":"mara@example.test","GIT_AUTHOR_DATE":"2026-10-05T12:00:00+00:00","GIT_COMMITTER_DATE":"2026-10-05T12:00:00+00:00"}
    subprocess.run(["git","-C",str(root),"revert","--no-edit","HEAD"],check=True,env=env,capture_output=True)
    write("auth/jwt.py","class JWTAuth:\n    def issue(self, subject):\n        return {'sub': subject}\n"); write("app.py","from auth.jwt import JWTAuth\n\ndef app():\n    return 'lantern'\n"); commit("Introduce JWT authentication",6)
    (root/"auth/legacy.py").unlink(); (root/"auth/session.py").unlink(); commit("Remove legacy authentication",7)
    write("migration.py","# TODO: migrate legacy account identifiers before v2\n\ndef migrate():\n    pass\n"); commit("Add TODO for account migration",8)
    write("services.py","# Service boundary\nclass AccountService:\n    def list_accounts(self):\n        return []\n"); commit("Refactor service layer",9)
    write("app.py","from auth.jwt import JWTAuth\nfrom services import AccountService\n\ndef app():\n    return AccountService()\n"); commit("Wire service layer",10)
    write("migration.py","# TODO: migrate legacy account identifiers before v2\n\ndef migrate():\n    # Keep this note until the import audit is complete.\n    pass\n"); commit("Document migration audit",11)
    git("switch","experiment/cache-layer")
    (root/"cache/sqlite_cache.py").unlink(); commit("Remove abandoned cache experiment",12)
    git("switch","main")
    git("switch","-c","feature/old-dashboard"); write("frontend/old_dashboard.py","# Unmerged dashboard branch\n"); commit("Sketch old dashboard route",13)
    git("switch","main")
    return str(root.resolve())

