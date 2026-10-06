#!/usr/bin/env python3
from pathlib import Path
import json,argparse,html,re,shutil
from common import read_fc
p=argparse.ArgumentParser();p.add_argument('--case',required=True);a=p.parse_args();case=Path(a.case).resolve();root=case.parent;d=json.loads(case.read_text());k=Path(__file__).resolve().parents[1]
if d.get('schema_version')!=1:p.error('Unsupported schema version')
project=d['project'];district=d['district_plan'];allowed={'verified','partial','not_found','unknown','not_applicable_verified'}
if district.get('status') not in allowed:p.error('Invalid district_plan.status')
if district['status'] in {'partial','not_found','unknown'} and not district.get('requested_from_user'):print('ACTION REQUIRED: request missing district-plan materials from the user; report remains preliminary')
def esc(v):return html.escape('미확인' if v is None else str(v),quote=True)
def safe_url(v):
 v=str(v or '');u=__import__('urllib.parse',fromlist=['urlsplit']).urlsplit(v)
 return v if (u.scheme in ('https','http') or not u.scheme and not v.startswith('//')) else '#'
def table(headers,rows):return '<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+esc(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table></div>'
facts=''.join('<div><small>'+esc(f['label'])+'</small><strong>'+esc(f.get('value'))+'</strong><span>'+esc(f.get('status','unverified'))+' · '+esc(f.get('source_id','출처 미기재'))+'</span></div>' for f in d.get('facts',[]))
sections=[]
for i,s in enumerate(d['sections'],1):
 body=''.join('<p>'+esc(x)+'</p>' for x in s.get('paragraphs',[]))
 for t in s.get('tables',[]):body+='<h3>'+esc(t.get('title',''))+'</h3>'+table(t['headers'],t['rows'])
 if not body:body='<p class="muted">자료 확인 및 분석 작성 전입니다.</p>'
 sections.append('<section id="section-'+str(i)+'"><div class="eyebrow">'+str(i).zfill(2)+'</div><h2>'+esc(s['title'])+'</h2>'+body+'</section>')
source_rows=[[s.get('id'),s.get('title'),s.get('checked_at'),s.get('note')] for s in d['sources']]
sources='<ul>'+''.join('<li>'+esc(s.get('id',''))+' · <a href="'+esc(safe_url(s.get('url','')))+'" target="_blank" rel="noopener">'+esc(s.get('title',''))+'</a> · '+esc(s.get('checked_at',''))+' · '+esc(s.get('note',''))+'</li>' for s in d['sources'])+'</ul>'
missing=' · '.join(district.get('missing',[])) or '목록 확인 전'
warning='<strong>지구단위계획: '+esc(district['status'])+'</strong><p>'+esc(district.get('summary',''))+'</p><p>자료 보완: '+esc(missing)+' / 사용자 요청: '+('완료' if district.get('requested_from_user') else '미실시')+'</p>'
values={'TITLE':esc(project.get('title')),'ADDRESS':esc(project.get('address')),'DATE':esc(project.get('checked_at')),'USES':esc(' · '.join(project.get('uses',[]))),'FACTS':facts,'DISTRICT':warning,'SECTIONS':''.join(sections),'SOURCES':sources}
report=(k/'assets/templates/report.html').read_text()
for key,val in values.items():report=report.replace('__'+key+'__',val)
(root/'report.html').write_text(report)
# All map content is embedded and credential-free. Only local files explicitly listed in the case are loaded.
def local_fc(value):
 if not value:return {'type':'FeatureCollection','features':[]}
 if isinstance(value,dict):return value
 path=(root/value).resolve()
 if not path.is_relative_to(root):raise ValueError('GeoJSON must be inside the case directory')
 return read_fc(path)
m=d.get('map',{});layers=[]
for layer in m.get('layers',[]):layers.append({**{kk:vv for kk,vv in layer.items() if kk!='path'},'geojson':local_fc(layer.get('path'))})
for i,ann in enumerate(m.get('annotations',[])):
 if ann.get('status') not in ['confirmed','calculated','assumption','unverified']:raise ValueError('Annotation status required')
 if ann.get('status')=='unverified' and ann.get('geojson'):raise ValueError('Do not draw an unverified regulatory line; use a map note')
 if ann.get('geojson') and not ann.get('source_id'):raise ValueError('Annotation source required')
 if ann.get('geojson'):layers.append({'id':'annotation-'+str(i),'label':ann['label']+' ['+ann['status']+']','color':ann.get('color','#d45a23'),'dash':ann['status']!='confirmed','geojson':local_fc(ann['geojson']),'source_id':ann['source_id'],'visible':True})
geo=local_fc(m.get('site_geojson'));center=project.get('center')
if center and (len(center)!=2 or not -180<=center[0]<=180 or not -85<=center[1]<=85):raise ValueError('Invalid WGS84 center')
data={'project':project,'center':center,'site':geo,'layers':layers,'notes':m.get('notes',[]),'reference_height_m':m.get('reference_height_m'),'reference_building':local_fc(m.get('reference_building_geojson'))}
encoded=json.dumps(data,ensure_ascii=False).replace('<',chr(92)+'u003c')
for name,target in [('map.html','map.html'),('vworld3d.html','map/vworld3d.html')]:
 text=(k/'assets/templates'/name).read_text().replace('__CASE_DATA__',encoded).replace('__ADDRESS__',esc(project['address']))
 path=root/target;path.parent.mkdir(exist_ok=True);path.write_text(text)
(root/'render-status.json').write_text(json.dumps({'district_plan':district['status'],'requested_from_user':district.get('requested_from_user',False),'map_features':len(geo['features']),'layers':len(layers),'is_legal_approval':False},ensure_ascii=False,indent=2))
print('Created report.html, map.html and map/vworld3d.html; browser verification still required')
