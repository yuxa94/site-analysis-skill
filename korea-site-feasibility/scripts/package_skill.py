#!/usr/bin/env python3
"""Make a shareable ZIP from explicit skill assets; never include a user's env."""
from pathlib import Path
import argparse,zipfile,re,urllib.parse as u
from common import keys
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--env');a=p.parse_args();root=Path(__file__).resolve().parents[1];target=Path(a.out).resolve()
if target.is_relative_to(root):p.error('Write ZIP outside the skill directory')
secrets=list(keys(a.env).values());patterns=[]
for s in secrets:
 if s:patterns.extend(x.encode() for x in {s,u.unquote(s),u.quote(s,safe=''),u.quote_plus(s)})
files=[];blocked=[]
for path in root.rglob('*'):
 if path.is_symlink():blocked.append(str(path.relative_to(root)));continue
 if not path.is_file():continue
 rel=path.relative_to(root)
 if any(n in {'__pycache__','node_modules','.git'} for n in rel.parts) or path.suffix in {'.pyc','.zip'}:continue
 if any(n.startswith('.env') for n in rel.parts) or path.suffix in {'.pem','.key'}:blocked.append(str(rel));continue
 body=path.read_bytes()
 if any(s in body for s in patterns):blocked.append(str(rel));continue
 try:text=body.decode('utf-8')
 except UnicodeDecodeError:text=''
 if re.search(r'/Users/[A-Za-z0-9_-]+/|/home/[A-Za-z0-9_-]+/|[A-Z]:\\Users\\[A-Za-z0-9_-]+',text):blocked.append(str(rel));continue
 files.append(path)
if blocked:p.error('Do not share: credential/private path or unsafe file detected in '+', '.join(blocked))
target.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
 for path in files:archive.write(path,Path(root.name)/path.relative_to(root))
print('Packaged',len(files),'files;',target.stat().st_size,'bytes; env/key files excluded')
