"""Generate private local Docker runtime settings; never print credential values."""
from pathlib import Path
import secrets

root = Path(__file__).resolve().parents[1]
destination = root / '.runtime/docker-stack.env'
if destination.exists():
    print('Existing private Docker settings retained.')
else:
    existing = {}
    for line in (root/'.env').read_text(encoding='utf-8-sig').splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            key, value = line.split('=',1)
            existing[key.strip()] = value.strip().strip('"').strip("'")
    if not existing.get('DB_PASSWORD'):
        raise SystemExit('DB_PASSWORD is missing from the local root .env.')
    settings = {'DB_PASSWORD':existing['DB_PASSWORD'],
                'JWT_SECRET':existing.get('JWT_SECRET') or secrets.token_urlsafe(48),
                'MONITORING_API_KEY':existing.get('MONITORING_API_KEY') or secrets.token_urlsafe(48),
                'GRAFANA_ADMIN_PASSWORD':existing.get('GRAFANA_ADMIN_PASSWORD') or secrets.token_urlsafe(24)}
    destination.parent.mkdir(parents=True,exist_ok=True)
    # Compose single quotes preserve dollar signs in existing passwords.
    def quote(value):
        if '\n' in value or '\r' in value:
            raise ValueError('Multiline credential values are not supported.')
        return "'" + value.replace('\\','\\\\').replace("'", "\\'") + "'"
    destination.write_text('\n'.join(f'{k}={quote(v)}' for k,v in settings.items())+'\n',encoding='utf-8')
    print('Private Docker runtime settings created; no credentials printed.')
