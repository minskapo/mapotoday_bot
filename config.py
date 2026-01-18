import os
from dotenv import load_dotenv

load_dotenv()

# 텔레그램 봇 설정
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8225463837:AAEAHLITWzQ2Zvr5sLsXEt8qx6KnF2O6_gA')

# 네이버 API 설정
NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')

# 봇 설정
CHAT_ID = os.getenv('CHAT_ID')  # 메시지를 받을 채팅 ID
SEARCH_QUERY = '마포'
DISPLAY_COUNT = 10  # API 절약을 위해 작은 값 사용
