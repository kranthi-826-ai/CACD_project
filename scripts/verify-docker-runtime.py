"""Run existing live checks against Docker/MySQL; credentials stay local."""
import ast
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ['docker','compose','-p','ai-pqc-security','--env-file',str(ROOT/'.runtime/docker-stack.env'),
           '-f',str(ROOT/'docker-compose.yml'),'-f',str(ROOT/'.runtime/docker-local.override.yml'),'--profile','app']
settings = {}
for line in (ROOT/'.runtime/docker-stack.env').read_text().splitlines():
    key, value = line.split('=',1)
    settings[key] = ast.literal_eval(value)
os.environ.update(settings)
sys.path.insert(0, str(ROOT/'tests/live'))
import verify_stack

def sql(query):
    command = COMPOSE + ['exec','-T','mysql','sh','-c',
        'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql --host=127.0.0.1 --user=root --batch --skip-column-names --execute "$1"', 'sh', query]
    result = subprocess.run(command,capture_output=True,text=True,timeout=15)
    if result.returncode:
        raise RuntimeError('Container MySQL read failed; no credentials or CLI stderr printed.')
    return result.stdout.strip()

verify_stack.sql = sql
out = ROOT/'ml/artifacts/docker-runtime-20261030'
out.mkdir(parents=True,exist_ok=True)
deadline = time.monotonic()+240
pending = {8761:'/actuator/health',8080:'/actuator/health',8081:'/actuator/health',8082:'/actuator/health',
           8083:'/actuator/health',8091:'/actuator/health',8090:'/health'}
while pending and time.monotonic()<deadline:
    for port,path in list(pending.items()):
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{port}{path}',timeout=3) as response:
                if json.load(response).get('status')=='UP':
                    pending.pop(port)
        except Exception:
            pass
    if pending:
        time.sleep(2)
if pending:
    raise SystemExit(f'Service readiness deadline; inspect containers on ports {list(pending)}.')
sys.argv = [sys.argv[0],'--output',str(out/'verification.json')]
verify_stack.main()
account = {'username':'docker_demo_'+secrets.token_hex(3),'password':secrets.token_urlsafe(24)}
status, _ = verify_stack.request('/api/v1/auth/register',body=account)
assert status==201
status, login = verify_stack.request('/api/v1/auth/login',body=account)
assert status==200
raw = (ROOT/'tests/e2e/bruno/AI-PQC-Security/Adaptive_Secure_Data.bru').read_text()
prototype,_ = json.JSONDecoder().raw_decode(raw.split('body:json {',1)[1].lstrip())
for name,sensitivity,q,h in [('classical','PUBLIC',False,False),('hybrid','RESTRICTED',False,True),('pqc','RESTRICTED',True,True)]:
    status,result = verify_stack.request('/api/v1/business/adaptive-secure-data',token=login['token'],
        body={**prototype,'dataSensitivity':sensitivity,'pqcSupported':q,'hybridSupported':h},correlation=f'docker-demo-{name}')
    assert status==200 and result['roundTripVerified']
(ROOT/'.runtime/docker-login.json').write_text(json.dumps(account,indent=2),encoding='utf-8')
print('Docker demonstration account and three verified mode executions ready. Credentials saved privately in .runtime/docker-login.json.')
