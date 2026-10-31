import json, os, urllib.request, urllib.error
from urllib.parse import urlsplit
from .models import Interpretation

MODEL=os.getenv("PHANTOMLEDGER_MODEL","gemma4:e4b")
OLLAMA_URL=os.getenv("PHANTOMLEDGER_OLLAMA_URL","http://localhost:11434").rstrip("/")
try:
    _OLLAMA_HOST=urlsplit(OLLAMA_URL).hostname
except ValueError:
    _OLLAMA_HOST=None
_OLLAMA_IS_LOCAL=_OLLAMA_HOST in {"localhost","127.0.0.1","::1"}


class GemmaUnavailable(RuntimeError): pass


def ollama_available() -> bool:
    if not _OLLAMA_IS_LOCAL:
        return False
    try:
        request=urllib.request.Request(OLLAMA_URL+"/api/tags")
        with urllib.request.urlopen(request,timeout=1.5) as response:
            return response.status == 200
    except Exception:
        return False


def interpret(memory: dict) -> Interpretation:
    if not _OLLAMA_IS_LOCAL:
        raise GemmaUnavailable("Gemma is unavailable. Showing the repository's verified history without AI interpretation.")
    evidence={"type":memory["type"],"title":memory["title"],"dates":memory["dates"],"authors":memory["authors"],"files":memory["files"],"commits":memory["commits"],"evidence":memory["evidence"],"summary":memory["summary"]}
    prompt=("You are a careful repository historian. Use ONLY this JSON evidence. Return only JSON with fields title, historical_summary, what_is_known (array), what_is_unknown (array), interpretation, confidence (high|medium|low). Do not invent facts, motives, dates, people, hashes, or files. If evidence is insufficient, explicitly say so. Keep interpretation concise.\nEVIDENCE:\n"+json.dumps(evidence,ensure_ascii=False))
    payload=json.dumps({"model":MODEL,"stream":False,"format":"json","messages":[{"role":"user","content":prompt}]}).encode()
    request=urllib.request.Request(OLLAMA_URL+"/api/chat",data=payload,headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(request,timeout=45) as response: raw=json.loads(response.read().decode())
        content=raw.get("message",{}).get("content","")
        return Interpretation.model_validate_json(content)
    except Exception as exc:
        raise GemmaUnavailable("Gemma is unavailable. Showing the repository's verified history without AI interpretation.") from exc

