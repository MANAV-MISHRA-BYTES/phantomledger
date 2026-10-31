from collections import defaultdict
from datetime import datetime
import re
import hashlib


def _dt(s):
    try: return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception: return None


def build_memories(data: dict) -> list[dict]:
    commits = data["commits"]
    ordered = sorted(commits, key=lambda c: c["date"])
    paths = defaultdict(list)
    for c in ordered:
        for change in c["changes"]: paths[change["file"]].append((c, change["status"]))
    result = []
    def add(kind,title,summary,events,files,score,evidence=None):
        events = sorted({e[0]["sha"]:e[0] for e in events}.values(), key=lambda c:c["date"])
        key = f"{kind}:{title}:{','.join(files)}"
        result.append({"id":hashlib.sha1(key.encode()).hexdigest()[:12],"type":kind,"title":title,"score":score,
          "summary":summary,"evidence": evidence or [f"{e['short_sha']} · {e['message']}" for e in events],
          "commits":[{k:e[k] for k in ("sha","short_sha","date","author","message")} for e in events],
          "files":sorted(set(files)),"dates":{"first":events[0]["date"] if events else None,"last":events[-1]["date"] if events else None},
          "authors":sorted({e["author"] for e in events}),"diff_summary":f"{len(events)} related commit(s) · {len(set(files))} file(s)"})
    for f, history in paths.items():
        add_del = [x for x in history if x[1].startswith("D")]
        adds = [x for x in history if x[1].startswith("A")]
        if add_del:
            add("Deleted file",f"The vanished file: {f}",f"{f} was removed from the repository history.",[(c,s) for c,s in history], [f],65)
            first_add=next((c for c,status in history if status.startswith("A")),None)
            if first_add:
                from pathlib import Path
                from .git_analyzer import git
                blob=git(Path(data["path"]),"show",f"{first_add['sha']}:{f}",check=False)
                lines=len(blob.splitlines())
                if lines>=40:
                    add("Large change later removed",f"A substantial addition disappeared: {f}",f"{f} was introduced with {lines} lines and later removed.",[(c,s) for c,s in history],[f],82)
        if len(history)>=3:
            add("Repeatedly modified",f"A file in constant motion: {f}",f"{f} appears in {len(history)} recorded file changes.",[(c,s) for c,s in history],[f],min(95,50+len(history)*4))
        if adds and add_del and _dt(add_del[-1][0]["date"]) and _dt(adds[0][0]["date"]):
            delta=(_dt(add_del[-1][0]["date"])-_dt(adds[0][0]["date"])).days
            if delta<=14:
                add("Short-lived experiment",f"The brief experiment: {f}",f"{f} was added and removed within {delta} day(s).",[(c,s) for c,s in history],[f],72)
    bymsg={c["message"].lower():c for c in commits}
    for c in commits:
        if c["message"].lower().startswith("revert "):
            add("Reverted change",f"A change was explicitly reverted",f"Commit {c['short_sha']} is titled as a revert.",[(c,"R")],c["files"],84)
    # TODO markers are scanned from tracked historical versions at commit snapshots, with git show (read only).
    found={}
    from .git_analyzer import git
    from pathlib import PurePosixPath
    repo_path=data["path"]
    for c in commits[:250]:
        for f in c["files"]:
            if f not in paths: continue
            out=git(__import__('pathlib').Path(repo_path),"show",f"{c['sha']}:{f}",check=False)
            for line_no,line in enumerate(out.splitlines(),1):
                if re.search(r"\b(TODO|FIXME)\b",line,re.I):
                    k=(f,line.strip())
                    found.setdefault(k,[]).append((c,"TODO"))
    for (f,line),events in found.items():
        unique={e[0]["sha"]:e for e in events}
        if len(unique)>=2:
            add("Long-lived TODO",f"An unresolved note in {f}",f"The marker “{line[:100]}” appears across {len(unique)} commits.",list(unique.values()),[f],75)
    # Ref branches with commits not reachable from current HEAD are dormant/abandoned candidates.
    from pathlib import Path
    head=set(__import__('subprocess').run(["git","-C",repo_path,"rev-list","HEAD"],capture_output=True,text=True).stdout.splitlines())
    for b in data["branches"]:
        tip=b.get("sha")
        if not tip or b.get("current"): continue
        full=__import__('subprocess').run(["git","-C",repo_path,"rev-parse",b["name"]],capture_output=True,text=True).stdout.strip()
        branch_commits=__import__('subprocess').run(["git","-C",repo_path,"rev-list",b["name"]],capture_output=True,text=True).stdout.splitlines()
        unique=[x for x in branch_commits if x not in head]
        if unique:
            mapped=[c for c in commits if c["sha"] in unique]
            add("Abandoned branch",f"Dormant branch: {b['name']}",f"{len(unique)} commit(s) on {b['name']} are not reachable from the current branch.",[(c,"B") for c in mapped], [f for c in mapped for f in c["files"]],78)
    for author in {c["author"] for c in ordered}:
        owned=[c for c in ordered if c["author"]==author]
        if len(ordered)>=3 and _dt(ordered[-1]["date"]) and _dt(owned[-1]["date"]):
            gap=(_dt(ordered[-1]["date"])-_dt(owned[-1]["date"])).days
            if gap>=30:
                add("Contributor inactivity",f"A contributor's last recorded change",f"{author}'s latest commit predates repository activity by {gap} day(s).",[(owned[-1],"C"), (ordered[-1],"C")],[],58)
    return sorted(result,key=lambda m:(-m["score"],m["dates"]["last"] or ""))

