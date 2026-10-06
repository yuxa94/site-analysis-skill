# 입력 양식과 보고서 템플릿

## 실행

스킬 경로를 `<SKILL>`로 두고 케이스 폴더를 따로 만든다.

```sh
python3 <SKILL>/scripts/init_case.py --out ./site-study --address '시·군·구 동 지번'
python3 <SKILL>/scripts/collect_public.py --case ./site-study/case.json --env ./.env
python3 <SKILL>/scripts/render_case.py --case ./site-study/case.json
python3 <SKILL>/scripts/serve_case.py --root ./site-study --env ./.env --port 8766
```

수집 전에 case.json의 PNU와 중심좌표를 검증해 채운다. 개인 Python 절대경로나 예시 좌표를 복사하지 않는다. Python3.9+와 curl, 웹 조사 도구가 필요하다. 스크립트는 외부 Python 라이브러리를 요구하지 않는다.

## case.json 작성

- `project`: title, address, pnu(19자리), checked_at(직접 확인일), uses(배열), center([경도,위도],WGS84).
- `facts`: `label`, `value`, `status`, `source_id`. 예: 현재 대지면적과 고시의 조건부 용적률을 다른 항목으로 둔다.
- `district_plan`: status, summary, sources(출처 ID), missing(누락도서), search_log(검색기관·검색어·URL·결과·일시), requested_from_user(실제로 요청한 경우만 true).
- `sections`: 각 장은 id, title, paragraphs(문자열 배열), tables(각 title/headers/rows)로 구성한다. 표 셀은 HTML이 아닌 일반 텍스트다. 내용 없는 장은 미작성으로 표시된다.
- `sources`: id, title, url(공식 URL 또는 케이스 내 상대경로), checked_at, note(필드/페이지/시행일/제약).
- `map.site_geojson`: 케이스 안 GeoJSON 상대경로 또는 FeatureCollection 객체.
- `map.layers`: id, label, path(케이스 내 GeoJSON 또는 VWorld 응답), color, visible, source_id. 원도 좌표는 EPSG:4326으로 변환한 뒤 넣는다. 미확보 레이어를 빈 도형의 ‘규제 없음’으로 해석하지 않는다.
- `map.annotations`: label, status, source_id, color, geojson. 고시 수치로 만든 선은 calculated와 방법 설명을 남긴다. 근거가 없는 미확정선은 geojson을 넣지 않고 notes에 상태를 적는다.
- `map.notes`: 지도 확인 수준·누락·현황시점 안내.
- `map.reference_building_geojson`, `reference_height_m`: 확인한 대상 건물 윤곽과 대장 높이. 둘 다 없으면 3D 참고 매스 비활성. 실제 입면 모델 아님.

출력 구조: 핵심판단 → 대지·면적 → 지도 → 입지 → 기존건물 → 지구단위·고시 → 법규 → 규모 → 비교안 → 주차·동선 → 설계 제안 → 근거. 일반 렌더러는 조사 결과를 표현하는 도구이며 법규 추론이나 규모계산을 자동 보증하지 않는다. 계산기·배경지도·원도 병렬 비교는 과업에 필요한 경우 예시 레이아웃을 참고하여 추가한다.

## 표현

밝은 종이색, 짙은 청록 본문, 주황색 참고·주의 색, 넓은 제목과 읽기 쉬운 표. 직접 확인/계산/가정/미확인을 색과 문구로 함께 구분한다. 모바일에서는 지도와 레이어가 세로로 배치되고 표는 가로 스크롤한다. 인쇄 시 조작 컨트롤을 숨긴다. 출처 ID는 각 근거와 연결한다.

2D 지도는 별도 서버 없이 작동한다. 실제3D는 전용 로컬 서버와 인터넷·키 필요. 서버는 localhost로만 연결하고 dotfile/디렉터리목록/env 파일을 노출하지 않는다. 다른 사람이 공유 ZIP을 받으면 본인의 키와 빈 포트를 사용한다.
