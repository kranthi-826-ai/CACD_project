"""Read-only web/proxy/monitoring checks; never print session credentials."""
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
def get(url, token=None):
    request = urllib.request.Request(url,headers={'Authorization':f'Bearer {token}'} if token else {})
    with urllib.request.urlopen(request,timeout=15) as response:
        return response.status,response.read()

account = json.loads((ROOT/'.runtime/docker-login.json').read_text())
login = urllib.request.Request('http://127.0.0.1:8088/api/v1/auth/login',data=json.dumps(account).encode(),headers={'Content-Type':'application/json'})
with urllib.request.urlopen(login,timeout=15) as response:
    token=json.load(response)['token']
status,who=get('http://127.0.0.1:8088/api/v1/auth/me',token)
assert status==200 and json.loads(who)['username']==account['username']
status,runs=get('http://127.0.0.1:8088/api/v1/business/executions',token)
runs=json.loads(runs)
assert {r['selectedMode'] for r in runs if r['roundTripVerified'] and r['outcome']=='SUCCESS'}=={'CLASSICAL','HYBRID','PQC'}
status,html=get('http://127.0.0.1:8088/')
assert status==200 and b'<div id="root">' in html
_,health=get('http://127.0.0.1:3000/api/health')
assert json.loads(health)['database']=='ok'
_,targets=get('http://127.0.0.1:9090/api/v1/targets')
targets=json.loads(targets)['data']['activeTargets']
assert len(targets)==7 and all(t['health']=='up' for t in targets)
report={'dashboard_http':200,'nginx_login_and_identity':'passed','three_modes_visible_through_dashboard_proxy':True,
        'grafana_database':'ok','prometheus_healthy_targets':len(targets),
        'scope':'HTTP/API checks, not interactive browser validation; email is not configured/verified.'}
(ROOT/'ml/artifacts/docker-runtime-20261030/web-monitoring.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
