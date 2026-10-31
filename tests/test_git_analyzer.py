import subprocess
from pathlib import Path
import pytest
from backend.git_analyzer import inspect_repository, validate_repo, GitError

def repo(tmp_path):
    p=tmp_path/'repo'; p.mkdir(); subprocess.run(['git','init','-b','main',str(p)],check=True,capture_output=True); subprocess.run(['git','-C',str(p),'config','user.name','Test']); subprocess.run(['git','-C',str(p),'config','user.email','test@example.com']); return p
def commit(p,msg):
    subprocess.run(['git','-C',str(p),'add','-A'],check=True); subprocess.run(['git','-C',str(p),'commit','-m',msg],check=True,capture_output=True)

def test_repository_detection_and_commits(tmp_path):
    p=repo(tmp_path); (p/'a.txt').write_text('one'); commit(p,'first')
    data=inspect_repository(str(p)); assert data['stats']['commits']==1; assert data['commits'][0]['message']=='first'
    with pytest.raises(GitError): validate_repo(str(tmp_path))

def test_branch_extraction(tmp_path):
    p=repo(tmp_path); (p/'a').write_text('a'); commit(p,'first'); subprocess.run(['git','-C',str(p),'switch','-c','experiment'],check=True,capture_output=True)
    (p/'b').write_text('b'); commit(p,'branch commit'); assert {b['name'] for b in inspect_repository(str(p))['branches']} >= {'main','experiment'}
