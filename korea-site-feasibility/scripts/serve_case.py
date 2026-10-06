#!/usr/bin/env python3
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
import argparse
from common import keys,request
p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--env');p.add_argument('--port',type=int,default=8766);a=p.parse_args();root=Path(a.root).resolve();env=Path(a.env).resolve() if a.env else None
if not (root/'report.html').exists():p.error('Render case first')
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kw):super().__init__(*args,directory=str(root),**kw)
 def log_message(self,*args):pass
 def list_directory(self,path):self.send_error(403);return None
 def do_GET(self):
  if self.headers.get('Host','').split(':')[0] not in ['127.0.0.1','localhost'] or self.headers.get('Sec-Fetch-Site')=='cross-site':self.send_error(403);return
  target=Path(self.translate_path(self.path)).resolve()
  if not target.is_relative_to(root) or any(x.startswith('.') for x in target.relative_to(root).parts) or (env and target==env):self.send_error(403);return
  if urlsplit(self.path).path=='/vworld-sdk.js':
   try:
    key=keys(a.env).get('VWORLD_KEY')
    if not key:raise ValueError('Missing key')
    # Runtime SDK needs credential; do not redact it here or write it to disk.
    body=request('https://map.vworld.kr/js/webglMapInit.js.do',{'version':'3.0','apiKey':key},[])
    body=body.replace("if(location.protocol == 'https:')","if(true)").encode()
    self.send_response(200);self.send_header('Content-Type','application/javascript; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
   except Exception:self.send_error(503,'VWorld SDK unavailable; check local API configuration')
  else:super().do_GET()
server=ThreadingHTTPServer(('127.0.0.1',a.port),Handler)
print(f'Local report: http://127.0.0.1:{server.server_port}/report.html',flush=True)
server.serve_forever()
