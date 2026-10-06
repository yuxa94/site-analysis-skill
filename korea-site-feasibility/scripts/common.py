from pathlib import Path
import os,json,subprocess,urllib.parse as u
ALLOWED={'api.vworld.kr','apis.data.go.kr','map.vworld.kr'}
def keys(env=None):
 d={}
 if env:
  for line in Path(env).read_text().splitlines():
   if '=' in line and not line.lstrip().startswith('#'):
    k,v=line.split('=',1);d[k.strip()]=v.strip().strip('"').strip("'")
 for k in ['VWORLD_KEY','DATA_GO_KR_KEY']:
  if os.environ.get(k):d[k]=os.environ[k]
 return d
def redact(body,secrets):
 for s in secrets:
  if s:
   for value in {s,u.unquote(s),u.quote(s,safe=''),u.quote_plus(s)}:body=body.replace(value,'[REDACTED]')
 return body
def request(base,params,secrets):
 if u.urlsplit(base).hostname not in ALLOWED or not base.startswith('https://'):raise ValueError('Unsupported API origin')
 url=base+('?' if params else '')+u.urlencode(params)
 try:
  r=subprocess.run(['curl','-fsS','--connect-timeout','10','--max-time','40','--config','-'],input='url = '+json.dumps(url)+'\n',capture_output=True,text=True)
 except OSError:raise RuntimeError('curl is required') from None
 if r.returncode:raise RuntimeError('API transport failure; inspect network/domain/key configuration without printing credentials')
 return redact(r.stdout,secrets)
def read_fc(path):
 d=json.loads(Path(path).read_text())
 if d.get('type')=='FeatureCollection':return d
 if d.get('type')=='Feature':return {'type':'FeatureCollection','features':[d]}
 return d.get('response',{}).get('result',{}).get('featureCollection',{'type':'FeatureCollection','features':[]})
