from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .models import RepositoryRequest, ChronicleRequest
from .git_analyzer import inspect_repository, GitError
from .memories import build_memories
from .demo_repo import create_demo
from .gemma import interpret, GemmaUnavailable, MODEL, ollama_available

app=FastAPI(title="PhantomLedger",version="1.0.0")
ROOT=Path(__file__).resolve().parents[1]
app.mount("/static",StaticFiles(directory=ROOT/"frontend"),name="static")
_cache={}

@app.get("/")
def home(): return FileResponse(ROOT/"frontend"/"index.html")

@app.get("/api/health")
def health(): return {"status":"ok","model":MODEL,"ollama_available":ollama_available()}

@app.post("/api/demo/create")
def demo():
    try: return {"path":create_demo()}
    except Exception as exc: raise HTTPException(500,f"Could not create demo repository: {exc}")

@app.post("/api/repository/inspect")
def inspect(req:RepositoryRequest):
    try:
        data=inspect_repository(req.path); _cache[data["path"]]=data
        return {"path":data["path"],"stats":data["stats"],"branches":data["branches"],"current_branch":data["current_branch"],"recent_commits":data["commits"][:12]}
    except (GitError,OSError,TimeoutError) as exc: raise HTTPException(400,str(exc))

@app.post("/api/repository/analyze")
def analyze(req:RepositoryRequest):
    try:
        data=inspect_repository(req.path); memories=build_memories(data); _cache[data["path"]]=data
        return {"path":data["path"],"stats":data["stats"],"branches":data["branches"],"commits":data["commits"],"memories":memories}
    except (GitError,OSError,TimeoutError) as exc: raise HTTPException(400,str(exc))

@app.get("/api/memories")
def memories(path:str):
    data=_cache.get(str(Path(path).resolve()))
    if not data: raise HTTPException(404,"Inspect or analyze this repository first.")
    return build_memories(data)

@app.get("/api/memories/{memory_id}")
def memory_detail(memory_id:str,path:str):
    data=_cache.get(str(Path(path).resolve()))
    if not data: raise HTTPException(404,"Inspect or analyze this repository first.")
    found=next((m for m in build_memories(data) if m["id"]==memory_id),None)
    if not found: raise HTTPException(404,"Memory not found.")
    return found

@app.post("/api/memories/{memory_id}/interpret")
def memory_interpret(memory_id:str,req:RepositoryRequest):
    data=_cache.get(str(Path(req.path).resolve()))
    if not data: raise HTTPException(404,"Analyze this repository first.")
    found=next((m for m in build_memories(data) if m["id"]==memory_id),None)
    if not found: raise HTTPException(404,"Memory not found.")
    try: return {"available":True,"interpretation":interpret(found).model_dump()}
    except GemmaUnavailable as exc: return {"available":False,"message":str(exc)}

@app.post("/api/chronicle")
def chronicle(req:ChronicleRequest):
    try:
        data=inspect_repository(req.path); memories=build_memories(data)
        return {"title":"Repository Chronicle","milestones":[{"date":m["dates"]["first"],"type":m["type"],"summary":m["summary"],"commit":m["commits"][0] if m["commits"] else None} for m in sorted(memories,key=lambda x:x["dates"]["first"] or "")[:12]]}
    except (GitError,OSError,TimeoutError) as exc: raise HTTPException(400,str(exc))
