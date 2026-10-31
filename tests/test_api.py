from fastapi.testclient import TestClient
from backend.main import app
from backend import gemma

client=TestClient(app)
def test_health_and_demo_analysis():
    assert client.get('/api/health').status_code==200
    demo=client.post('/api/demo/create',json={}); assert demo.status_code==200
    result=client.post('/api/repository/analyze',json={'path':demo.json()['path']}); assert result.status_code==200
    assert result.json()['memories']

def test_ollama_unavailable(monkeypatch,tmp_path):
    from backend.demo_repo import create_demo
    p=create_demo(str(tmp_path/'demo')); a=client.post('/api/repository/analyze',json={'path':p}).json()
    m=next(x for x in a['memories'] if x['type']=='Reverted change')
    monkeypatch.setattr(gemma,'interpret',lambda _: (_ for _ in ()).throw(gemma.GemmaUnavailable("Gemma is unavailable. Showing the repository's verified history without AI interpretation.")))
    out=client.post(f"/api/memories/{m['id']}/interpret",json={'path':p})
    assert out.status_code==200 and out.json()['available'] is False

def test_pydantic_interpretation_validation():
    from pydantic import ValidationError
    from backend.models import Interpretation
    Interpretation.model_validate({'title':'x','historical_summary':'s','what_is_known':[],'what_is_unknown':[],'interpretation':'i','confidence':'low'})
    try: Interpretation.model_validate({'title':'x','confidence':'certain'})
    except ValidationError: pass
    else: raise AssertionError('Invalid AI result was accepted')

def test_remote_ollama_url_is_never_contacted(monkeypatch):
    monkeypatch.setattr(gemma,'_OLLAMA_IS_LOCAL',False)
    assert gemma.ollama_available() is False
    try: gemma.interpret({'type':'test'})
    except gemma.GemmaUnavailable: pass
    else: raise AssertionError('A remote Ollama endpoint was allowed')
