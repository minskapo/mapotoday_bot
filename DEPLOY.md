# 클라우드 배포 가이드

PC를 켜지 않아도 봇이 24시간 실행되도록 클라우드 서비스에 배포하는 방법입니다.

## 🚀 Railway 배포 (추천 - 무료 티어 제공)

Railway는 가장 간단하고 무료 티어를 제공하는 서비스입니다.

### 1단계: Railway 계정 생성

1. https://railway.app 접속
2. GitHub 계정으로 로그인 (또는 이메일로 가입)

### 2단계: 프로젝트 배포

1. Railway 대시보드에서 "New Project" 클릭
2. "Deploy from GitHub repo" 선택
3. GitHub 저장소 선택 (또는 먼저 GitHub에 코드 업로드)
4. 저장소가 없다면:
   ```bash
   cd /Users/minski/dev/mapotoday_bot
   git init
   git add .
   git commit -m "Initial commit"
   # GitHub에 새 저장소 생성 후
   git remote add origin https://github.com/yourusername/mapotoday_bot.git
   git push -u origin main
   ```

### 3단계: 환경 변수 설정

Railway 대시보드에서:
1. 프로젝트 선택 → "Variables" 탭 클릭
2. 다음 환경 변수 추가:
   - `TELEGRAM_BOT_TOKEN`: 텔레그램 봇 토큰
   - `NAVER_CLIENT_ID`: 네이버 API Client ID
   - `NAVER_CLIENT_SECRET`: 네이버 API Client Secret
   - `CHAT_ID`: 텔레그램 채팅 ID

### 4단계: 배포 확인

1. Railway가 자동으로 배포를 시작합니다
2. "Deployments" 탭에서 로그 확인
3. 배포가 완료되면 봇이 자동으로 실행됩니다

### 5단계: 로그 확인

Railway 대시보드의 "Deployments" → "View Logs"에서 실시간 로그 확인 가능

---

## 🌐 Render 배포 (대안)

Render도 무료 티어를 제공합니다.

### 1단계: Render 계정 생성

1. https://render.com 접속
2. GitHub 계정으로 로그인

### 2단계: 새 Web Service 생성

1. "New +" → "Web Service" 선택
2. GitHub 저장소 연결
3. 설정:
   - **Name**: mapotoday-bot
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`

### 3단계: 환경 변수 설정

"Environment" 섹션에서 환경 변수 추가:
- `TELEGRAM_BOT_TOKEN`
- `NAVER_CLIENT_ID`
- `NAVER_CLIENT_SECRET`
- `CHAT_ID`

### 4단계: 배포

"Create Web Service" 클릭하여 배포 시작

---

## 📝 주의사항

1. **무료 티어 제한**:
   - Railway: 월 $5 크레딧 (충분함)
   - Render: 15분 비활성 시 슬립 모드 (웹훅 필요)

2. **파일 저장소**:
   - `processed_articles.json`과 `subscribed_chats.txt`는 Railway의 임시 저장소에 저장됩니다
   - 서비스 재시작 시 초기화될 수 있으므로, 필요시 외부 저장소(DB) 사용 고려

3. **환경 변수**:
   - `.env` 파일은 Git에 커밋하지 마세요
   - 클라우드 서비스의 환경 변수 설정만 사용합니다

---

## 🔄 업데이트 방법

코드를 수정한 후:
```bash
git add .
git commit -m "Update bot"
git push
```

Railway/Render가 자동으로 재배포합니다.

---

## 🛑 배포 중지

Railway/Render 대시보드에서 서비스를 일시 중지하거나 삭제할 수 있습니다.
