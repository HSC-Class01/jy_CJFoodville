# OpenDART API 설정

GitHub 저장소의 Settings → Secrets and variables → Actions → New repository secret에서 다음을 추가합니다.

- Name: DART_API_KEY
- Value: OpenDART에서 발급받은 40자리 인증키

API 키는 코드나 CSV에 저장하지 않습니다.

최초 실행: Actions → DART Financial Update → Run workflow.
자동 실행: 매월 1일 01:00 KST. GitHub Actions는 UTC 기준이므로 cron은 0 16 1 * * 입니다.
