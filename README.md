# CJ푸드빌 DART Financial Agent

🔗 대시보드 바로가기: https://hsc-class01.github.io/jy_CJFoodville/

![Dashboard](https://img.shields.io/badge/Dashboard-Open-blue?style=for-the-badge)

CJ푸드빌의 DART/OpenDART 정기보고서를 수집하고 주요 재무수치와 재무비율을 계산하여 GitHub Pages 대시보드에 표시하는 자동화 프로젝트입니다.

## 자동화 범위
- 대상: CJ푸드빌(주), OpenDART 법인고유번호 00357120
- 수집 시작: 2010년
- 보고서: 사업보고서, 반기보고서, 1분기보고서, 3분기보고서
- 연결재무제표(CFS) 우선
- 매월 1일 01:00 KST 자동 실행
- Actions에서 수동 실행 가능
- Dashboard: GitHub Pages

## 2010~2014년 데이터
OpenDART 공식 개발가이드상 정기보고서 재무정보 API는 2015년 이후 제공됩니다. 따라서 2010~2014년은 공시검색 API로 보고서 메타데이터와 접수번호를 보존하고, 2015년 이후는 재무제표 API로 수치까지 추출합니다. 제공범위 밖의 과거 수치는 임의로 생성하지 않습니다.

## API Key
OpenDART에서 인증키를 발급한 후 GitHub Settings → Secrets and variables → Actions에 DART_API_KEY라는 Repository secret으로 저장합니다. 코드에는 API 키를 넣지 않습니다.

## 주요 수치
매출액, 매출총이익, 영업이익, 법인세비용차감전순이익, 당기순이익, 총자산, 유동자산, 총부채, 유동부채, 자본총계, 현금및현금성자산, 재고자산, 매출채권, 매입채무, 영업활동현금흐름, 이자비용, 감가상각비.

## 주요 비율
매출증가율, 영업이익률, 순이익률, 부채비율, 자기자본비율, 유동비율, 당좌비율, ROA, ROE, 이자보상배율.

## 국내 Peer Firms
| 기업 | 주요 비교영역 |
|---|---|
| 파리크라상 | 베이커리·프랜차이즈·외식 |
| (유)아웃백스테이크하우스코리아 | 외식·레스토랑 |
| 한화푸드테크(주) | 외식·푸드서비스 |
| (주)엠에프지코리아 | 외식·레스토랑 |
| 아모제푸드(주) | 외식·푸드서비스 |

Peer는 사업영역 비교용 기업군이며 투자목적의 순위·등급을 의미하지 않습니다.

## 구조
.github/workflows/update-dart.yml
config/company.json
data/raw/filings.json
data/processed/annual.csv
data/processed/half_year.csv
data/processed/quarterly.csv
docs/API_SETUP.md
scripts/dart_agent.py
dashboard/index.html
requirements.txt
README.md
