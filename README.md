# 마포 오늘 뉴스 텔레그램 봇

네이버 뉴스 API를 사용하여 '마포' 키워드가 포함된 최신 뉴스를 5분마다 자동으로 텔레그램으로 전송하는 봇입니다.

## 기능

- ✅ 5분마다 자동으로 '마포' 키워드 뉴스 검색
- ✅ 중복 기사 자동 필터링
- ✅ 기사 제목을 클릭하면 원문 링크로 이동
- ✅ API 호출 최적화 (최소한의 호출로 최신 기사만 가져오기)

---

## 📋 사용 방법 (단계별 가이드)

### 1단계: Python 환경 확인

Python 3.7 이상이 설치되어 있어야 합니다.

```bash
python --version
# 또는
python3 --version
```

### 2단계: 필요한 패키지 설치

`mapotoday_bot` 폴더에서 다음 명령어를 실행하세요:

```bash
cd mapotoday_bot
pip install -r requirements.txt
```

또는 Python 3를 사용하는 경우:

```bash
pip3 install -r requirements.txt
```

### 3단계: 네이버 API 인증 정보 얻기

1. **네이버 개발자 센터 접속**
   - https://developers.naver.com/ 접속
   - 네이버 계정으로 로그인

2. **애플리케이션 등록**
   - 상단 메뉴에서 "Application" → "애플리케이션 등록" 클릭
   - 애플리케이션 이름 입력 (예: "마포뉴스봇")
   - 사용 API: **"검색"** 선택
   - 비로그인 오픈API 서비스 환경: **"WEB 설정"** 선택
     - 서비스 URL: `http://localhost` (임시로 입력해도 됨)
     - 로컬 PC에서 사용할 경우: `http://localhost` 또는 `http://127.0.0.1`

3. **Client ID와 Client Secret 확인**
   - 등록 완료 후 "내 애플리케이션" 메뉴에서 등록한 애플리케이션 클릭
   - **Client ID**와 **Client Secret** 복사

### 4단계: 텔레그램 채팅 ID 확인

봇이 메시지를 보낼 채팅 ID를 확인해야 합니다.

#### 방법 1: 개인 채팅 (자신에게 보내기)

1. 텔레그램에서 `@userinfobot` 검색
2. 봇에게 아무 메시지나 전송 (예: `/start`)
3. 봇이 응답으로 보내는 정보에서 **"Id"** 값 확인
   - 예: `Id: 123456789` → `123456789`가 채팅 ID

#### 방법 2: 그룹 채팅

1. 그룹에 `@userinfobot` 추가
2. 봇에게 `/start` 명령 전송
3. 봇이 응답으로 보내는 그룹 ID 확인
   - 그룹 ID는 보통 음수입니다 (예: `-1001234567890`)

#### 방법 3: 채널

1. 채널에 봇을 관리자로 추가
2. 채널 ID는 보통 `-100`으로 시작하는 숫자입니다
3. `@getidsbot` 같은 봇을 사용하여 확인 가능

### 5단계: 환경 변수 설정

`mapotoday_bot` 폴더에 `.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
TELEGRAM_BOT_TOKEN=8225463837:AAEAHLITWzQ2Zvr5sLsXEt8qx6KnF2O6_gA
NAVER_CLIENT_ID=여기에_네이버_Client_ID_입력
NAVER_CLIENT_SECRET=여기에_네이버_Client_Secret_입력
CHAT_ID=여기에_텔레그램_채팅_ID_입력
```

**예시:**
```env
TELEGRAM_BOT_TOKEN=8225463837:AAEAHLITWzQ2Zvr5sLsXEt8qx6KnF2O6_gA
NAVER_CLIENT_ID=abc123def456ghi789
NAVER_CLIENT_SECRET=xyz789uvw456rst123
CHAT_ID=123456789
```

> ⚠️ **주의**: `.env` 파일은 개인정보가 포함되어 있으므로 절대 Git에 커밋하지 마세요!

### 6단계: 봇 실행

`mapotoday_bot` 폴더에서 다음 명령어를 실행하세요:

```bash
cd mapotoday_bot
python bot.py
```

또는 이미 `mapotoday_bot` 폴더 안에 있다면:
```bash
python bot.py
```

또는:

```bash
python3 bot.py
```

**정상 실행 시 출력 예시:**
```
마포 오늘 뉴스 봇을 시작합니다...
검색어: 마포
체크 간격: 5분
구독자 수: 1
[2026-01-18 16:30:00] 뉴스 확인 중...
새로운 기사가 없습니다.
```

### 7단계: 봇 중지

봇을 중지하려면 터미널에서 `Ctrl + C`를 누르세요.

---

## 📁 파일 구조

```
.
├── bot.py                      # 메인 봇 로직
├── naver_api.py                # 네이버 뉴스 API 클라이언트
├── config.py                   # 설정 관리
├── requirements.txt            # 필요한 패키지 목록
├── .env                        # 환경 변수 (직접 생성)
├── .gitignore                  # Git 제외 파일 목록
├── README.md                   # 이 파일
├── processed_articles.json     # 처리된 기사 ID 저장 (자동 생성)
└── subscribed_chats.txt        # 구독한 채팅 ID 목록 (자동 생성)
```

---

## 🔧 문제 해결

### 오류: "TELEGRAM_BOT_TOKEN 환경 변수가 설정되지 않았습니다."

**해결 방법:**
- `.env` 파일이 `mapotoday_bot` 폴더에 있는지 확인
- `.env` 파일에 `TELEGRAM_BOT_TOKEN`이 올바르게 입력되었는지 확인

### 오류: "네이버 API 인증 정보가 설정되지 않았습니다."

**해결 방법:**
- `.env` 파일에 `NAVER_CLIENT_ID`와 `NAVER_CLIENT_SECRET`이 올바르게 입력되었는지 확인
- 네이버 개발자 센터에서 애플리케이션이 정상적으로 등록되었는지 확인

### 오류: "구독자가 없습니다."

**해결 방법:**
- `.env` 파일에 `CHAT_ID`가 올바르게 입력되었는지 확인
- 텔레그램 채팅 ID를 다시 확인 (음수인 경우 `-` 기호 포함)

### 메시지가 전송되지 않습니다

**확인 사항:**
1. 텔레그램 봇 토큰이 올바른지 확인
2. 채팅 ID가 올바른지 확인
3. 봇이 해당 채팅에 접근 권한이 있는지 확인 (개인 채팅의 경우 봇에게 먼저 메시지를 보내야 함)
4. 네이버 API 호출이 정상적으로 되는지 확인 (터미널 로그 확인)

### API 호출 오류

**확인 사항:**
1. 네이버 API 인증 정보가 올바른지 확인
2. 네이버 개발자 센터에서 애플리케이션의 API 사용량 제한 확인
3. 인터넷 연결 상태 확인

---

## ⚙️ 설정 변경

### 검색 키워드 변경

`bot.py` 파일의 다음 줄을 수정하세요:

```python
SEARCH_QUERY = '마포'  # 원하는 키워드로 변경
```

### 검색 간격 변경

`bot.py` 파일의 `run()` 메서드에서 다음 줄을 수정하세요:

```python
schedule.every(5).minutes.do(self.check_and_send_news)  # 5를 원하는 분으로 변경
```

예: 10분마다 실행하려면 `schedule.every(10).minutes.do(...)`

### 검색 결과 개수 변경

`bot.py` 파일의 다음 줄을 수정하세요:

```python
DISPLAY_COUNT = 10  # 원하는 개수로 변경 (10~100 사이)
```

---

## 📝 주의사항

- ⚠️ 봇이 실행되면 5분마다 자동으로 뉴스를 확인하고 전송합니다.
- ⚠️ 중복 기사는 자동으로 필터링됩니다.
- ⚠️ API 호출을 절약하기 위해 한 번에 10개의 기사만 검색합니다.
- ⚠️ 봇을 중지하려면 `Ctrl+C`를 누르세요.
- ⚠️ `.env` 파일은 절대 공유하거나 Git에 커밋하지 마세요!

---

## 💡 팁

- 봇을 백그라운드에서 실행하려면 `nohup` 또는 `screen`을 사용하세요:
  ```bash
  cd mapotoday_bot
  nohup python bot.py > bot.log 2>&1 &
  ```
- 로그를 파일로 저장하려면:
  ```bash
  cd mapotoday_bot
  python bot.py > bot.log 2>&1
  ```

---

## ☁️ 클라우드 배포 (PC를 켜지 않아도 24시간 실행)

PC를 끄더라도 봇이 계속 실행되도록 클라우드 서비스에 배포할 수 있습니다.

### 빠른 배포 (Railway 추천)

1. **Railway 계정 생성**: https://railway.app
2. **GitHub에 코드 업로드** (선택사항)
3. **Railway에서 프로젝트 배포**
4. **환경 변수 설정**: Railway 대시보드에서 `.env` 파일의 내용을 환경 변수로 추가

자세한 배포 방법은 [DEPLOY.md](DEPLOY.md) 파일을 참고하세요.

### 배포 후 장점

- ✅ PC를 끄더라도 봇이 계속 실행됩니다
- ✅ 24시간 자동으로 기사를 확인하고 전송합니다
- ✅ 무료 티어로 충분히 사용 가능합니다
- ✅ 코드 업데이트 시 자동 재배포됩니다
