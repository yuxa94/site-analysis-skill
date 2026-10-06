# 데이터 수집과 동일성 검증

아래는 상봉동 예시에서 사용한 경로다. 실행 시 공식 API 문서, 사용자 승인 서비스와 응답 상태를 확인한다. 서비스 이전·필드 변경은 관찰한 근거로 수정한다.

## 공공데이터포털

HTTPS `https://apis.data.go.kr/1613000/` 아래:
- `BldRgstHubService`: `getBrRecapTitleInfo`, `getBrTitleInfo`, `getBrFlrOulnInfo`, `getBrAtchJibunInfo`.
- `ArchPmsHubService`: `getApBasisOulnInfo`, `getApPklotInfo`.
- `HsPmsHubService`: `getHpBasisOulnInfo`.

공통: `serviceKey`, `sigunguCd`, `bjdongCd`, `platGbCd`(일반0/산1), `bun`, `ji`, `numOfRows`, `pageNo`, `_type=json`. PNU의 토지구분 코드와 platGbCd 숫자를 그대로 혼동하지 않는다. 인증키는 URL 인코딩 전/후 중 어떤 키인지 확인하여 한 번만 인코딩한다. HTTP200만 성공으로 판정하지 않는다. 서비스 resultCode와 건수·페이지를 함께 기록한다. 0건은 정상 조회의 공백일 수 있으며 허가 부존재나 오류라고 단정하지 않는다.

## 브이월드

- 주소 좌표: `https://api.vworld.kr/req/address` / `service=address&request=getCoord&version=2.0&type=parcel`.
- 도형: `https://api.vworld.kr/req/data` / `service=data&request=GetFeature&version=2.0&crs=EPSG:4326&geometry=true`.
- 대상 필지: `data=LP_PA_CBND_BUBUN&attrFilter=pnu:=:<검증한PNU>`.
- 토지특성 `https://api.vworld.kr/ned/data/getLandCharacteristics`, 규제속성 `https://api.vworld.kr/ned/data/getLandUseAttr`.
- 주변: `geomFilter=BOX(minLon,minLat,maxLon,maxLat)`로 필요한 범위를 정하고 페이지·전체 건수를 확인한다. 무제한 전국 수집을 하지 않는다.

| 레이어 | 내용 |
|---|---|
| LP_PA_CBND_BUBUN | 연속지적도 |
| LT_C_UQ111 | 용도지역 |
| LT_C_UPISUQ161 | 지구단위계획구역 |
| LT_C_UPISUQ151 | 도시계획도로 |
| LT_C_UPISUQ152 | 도시계획 철도 |
| LT_C_SPBD | 도로명주소 건물 윤곽·층수 |
| LT_C_UO101 | 교육환경보호구역 |

레이어가 신청·제공되지 않을 수 있다. 응답을 기록하고 실패 레이어를 ‘규제 없음’으로 표시하지 않는다. 도시계획 도로/철도 폴리곤은 실제 도로 경계·지하구조물·철도보호구역과 다르다. ‘접함’은 대상지 포함이 아니다.

2D 배경이 필요하면 공식 WMTS Base/Satellite 타일을 조회하고 EPSG:3857의 타일 범위에 정확히 배치한다. 배경 제작/촬영일과 조회일을 구분한다. 템플릿 기본은 키 없는 벡터 지도이며 배경이 없는 상태를 설명한다.

## 토지이음

공식 `https://www.eum.go.kr`에서 주소 검색. PNU만 넣은 링크 결과를 믿지 말고 화면 주소·지목·면적·PNU를 대조한다. 정상 열람 화면의 확인도면·규제표·열람일·URL을 저장한다. 확인도면 이미지 URL은 세션성일 수 있으므로 실제 표시된 자산을 저장하거나 정상 캡처한다. 인증·캡차 우회 금지. 브라우저 도구가 없다면 공식 공개 경로로 확인하고 열람 불가를 기록한다.

## 인증키와 네트워크

키는 사용자 환경 변수 또는 지정한 env 파일에서만 읽는다. `curl`에는 URL을 표준입력 config로 전달하여 명령행 키 노출을 피한다. curl 에러 원문·인증 URL을 대화/파일에 출력하지 않는다. 응답에 키가 반사되면 저장 전 치환한다. SSL 검증을 끄지 않는다. 키 만료·도메인 제한과 자료 0건을 구분한다. 다른 기관·도메인에 키를 전송하지 않는다.

보조 수집기는 기본 5페이지 상한이며 상한 초과 시 `truncated`로 표시한다. 전체가 필요하면 범위를 좁히거나 명시적으로 max-pages를 높인다. 대장 여러 건은 관리번호·사용승인일·멸실/이력·동별 등록 단위로 대조하여 현 건물을 선택한다.
