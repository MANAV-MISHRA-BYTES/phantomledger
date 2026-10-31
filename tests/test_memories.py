import subprocess
from backend.git_analyzer import inspect_repository
from backend.memories import build_memories
from backend.demo_repo import create_demo

def test_demo_produces_required_memories(tmp_path):
    p=create_demo(str(tmp_path/'haunted')); types={m['type'] for m in build_memories(inspect_repository(p))}
    assert 'Deleted file' in types
    assert 'Reverted change' in types
    assert 'Abandoned branch' in types
    assert 'Long-lived TODO' in types
    assert 'Repeatedly modified' in types

def test_memory_score_is_bounded_and_sorted(tmp_path):
    data=inspect_repository(create_demo(str(tmp_path/'haunted'))); ms=build_memories(data)
    assert ms and all(0<=m['score']<=100 for m in ms)
    assert [m['score'] for m in ms]==sorted((m['score'] for m in ms),reverse=True)
