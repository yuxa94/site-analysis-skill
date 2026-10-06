#!/usr/bin/env python3
"""Bounded, read-only collection. Saves redacted responses; never declares legal applicability."""
from pathlib import Path
import argparse,json,re,math,urllib.parse as u
from common import keys,request
p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--env');p.add_argument('--radius-m',type=float,default=250);p.add_argument('--max-pages',type=int,default=5);a=p.parse_args()
if not 10<=a.radius_m<=2000 or not 1<=a.max_pages<=100:p.error('radius must be 10–2000m; max-pages 1–100')
case=Path(a.case).resolve();d=json.loads(case.read_text());proj=d['project'];pnu=proj.get('pnu') or ''
if not re.fullmatch(r'[0-9]{19}',pnu) or pnu[10] not in '12':p.error('Verify a 19-digit PNU with land division 1 or 2 before collection')
creds=keys(a.env);secret=list(creds.values());out=case.parent/'sources';out.mkdir(exist_ok=True);jobs=[];summary=[]
vk=creds.get('VWORLD_KEY');dk=creds.get('DATA_GO_KR_KEY')
if vk:
 common=dict(key=vk,format='json')
 jobs += [('geocode','https://api.vworld.kr/req/address',dict(common,service='address',request='getCoord',version='2.0',address=proj['address'],type='parcel'),'single'),('parcel','https://api.vworld.kr/req/data',dict(common,service='data',request='GetFeature',version='2.0',data='LP_PA_CBND_BUBUN',attrFilter='pnu:=:'+pnu,geometry='true',crs='EPSG:4326',size=100),'feature'),('land','https://api.vworld.kr/ned/data/getLandCharacteristics',dict(common,pnu=pnu,numOfRows=100),'ned'),('landuse','https://api.vworld.kr/ned/data/getLandUseAttr',dict(common,pnu=pnu,numOfRows=100),'ned')]
 c=proj.get('center')
 if c and len(c)==2:
  x,y=c;dy=a.radius_m/111320;dx=dy/math.cos(math.radians(y));bbox=f'BOX({x-dx},{y-dy},{x+dx},{y+dy})'
  for layer in ['LP_PA_CBND_BUBUN','LT_C_UQ111','LT_C_UPISUQ161','LT_C_UPISUQ151','LT_C_UPISUQ152','LT_C_SPBD','LT_C_UO101']:
   jobs.append((layer.lower(),'https://api.vworld.kr/req/data',dict(common,service='data',request='GetFeature',version='2.0',data=layer,geomFilter=bbox,geometry='true',crs='EPSG:4326',size=1000),'feature'))
if dk:
 for service,ops in [('BldRgstHubService',['getBrRecapTitleInfo','getBrTitleInfo','getBrFlrOulnInfo','getBrAtchJibunInfo']),('ArchPmsHubService',['getApBasisOulnInfo','getApPklotInfo']),('HsPmsHubService',['getHpBasisOulnInfo'])]:
  for op in ops:jobs.append((op,'https://apis.data.go.kr/1613000/'+service+'/'+op,dict(serviceKey=u.unquote(dk),sigunguCd=pnu[:5],bjdongCd=pnu[5:10],platGbCd='0' if pnu[10]=='1' else '1',bun=pnu[11:15],ji=pnu[15:19],numOfRows=100,_type='json'),'hub'))
if not jobs:p.error('No API keys configured; proceed with public web research or supply an env file')
for name,url,params,kind in jobs:
 rec={'name':name,'pages':0,'status':'unknown','truncated':False};features=[]
 try:
  for page in range(1,a.max_pages+1):
   q=dict(params)
   if kind!='single':q['page' if kind=='feature' else 'pageNo']=page
   body=request(url,q,secret);suffix='' if page==1 else f'_page{page}'
   try:r=json.loads(body)
   except json.JSONDecodeError:
    (out/(name+suffix+'.xml')).write_text(body);rec['status']='non_json_response';break
   (out/(name+suffix+'.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2));rec['pages']=page
   response=r.get('response',{})
   if kind=='feature':
    rec['status']=response.get('status','unknown');features+=response.get('result',{}).get('featureCollection',{}).get('features',[]);total_pages=int(response.get('page',{}).get('total',1))
   elif kind=='hub':
    rec['status']=str(response.get('header',{}).get('resultCode','unknown'));total=int(response.get('body',{}).get('totalCount',0));total_pages=max(1,math.ceil(total/100));rec['total_count']=total
   elif kind=='ned':
    obj=next((v for v in r.values() if isinstance(v,dict) and ('totalCount' in v or 'field' in v)),{});total=int(obj.get('totalCount',0));total_pages=max(1,math.ceil(total/100));rec['status']='received_requires_review';rec['total_count']=total
   else:rec['status']=response.get('status','received_requires_review');total_pages=1
   if page>=total_pages:break
   if page==a.max_pages:rec['truncated']=True
  if kind=='feature' and features:(out/(name+'.geojson')).write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False))
 except (RuntimeError,ValueError,TypeError,KeyError):rec['status']='failed_requires_review'
 summary.append(rec);print(name,rec['status'],'pages',rec['pages'],'truncated',rec['truncated'])
(out/'collection_status.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print('Saved redacted evidence. Verify identities, API codes, missing layers, pagination and legal sources before reporting.')
