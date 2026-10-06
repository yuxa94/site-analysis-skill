#!/usr/bin/env python3
from pathlib import Path
import argparse,json,datetime
p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--address',required=True);a=p.parse_args()
out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
if (out/'case.json').exists():p.error('case.json already exists; choose a new case folder')
k=Path(__file__).resolve().parents[1];d=json.loads((k/'assets/blank-case.json').read_text())
d['project'].update(address=a.address,checked_at=datetime.date.today().isoformat())
(out/'case.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');(out/'sources').mkdir(exist_ok=True)
print('Created case.json; verify PNU and center before collection')
