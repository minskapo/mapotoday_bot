import os
import time
import schedule
import asyncio
import warnings
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError
from naver_api import NaverNewsAPI

# urllib3 경고 숨기기
warnings.filterwarnings('ignore', category=UserWarning, module='urllib3')


# 환경 변수 로드
load_dotenv()

# 설정
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8225463837:AAEAHLITWzQ2Zvr5sLsXEt8qx6KnF2O6_gA')
NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')
CHAT_ID = os.getenv('CHAT_ID')  # 봇이 메시지를 보낼 채팅 ID (선택사항)
SEARCH_QUERY = '마포'
DISPLAY_COUNT = 10  # API 절약을 위해 작은 값 사용


class MapoTodayBot:
    """마포 오늘 뉴스 텔레그램 봇"""
    
    def __init__(self):
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN 환경 변수가 설정되지 않았습니다.")
        if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
            raise ValueError("네이버 API 인증 정보가 설정되지 않았습니다.")
        
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.naver_api = NaverNewsAPI(NAVER_CLIENT_ID, NAVER_CLIENT_SECRET)
        self.chat_id = CHAT_ID
        self.subscribed_chats = set()
        self._load_subscribed_chats()
        # 비동기 루프 초기화
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
    
    def _load_subscribed_chats(self):
        """구독한 채팅 ID 목록 로드"""
        if os.path.exists('subscribed_chats.txt'):
            try:
                with open('subscribed_chats.txt', 'r', encoding='utf-8') as f:
                    for line in f:
                        chat_id = line.strip()
                        if chat_id:
                            self.subscribed_chats.add(chat_id)
            except:
                pass
        
        # 환경 변수에 CHAT_ID가 있으면 추가 (정수로 변환)
        if self.chat_id:
            try:
                # 문자열인 경우 정수로 변환
                chat_id_int = int(self.chat_id)
                self.subscribed_chats.add(str(chat_id_int))  # 문자열로 저장 (일관성 유지)
            except (ValueError, TypeError):
                # 변환 실패 시 그대로 사용
                self.subscribed_chats.add(str(self.chat_id))
    
    def _save_subscribed_chats(self):
        """구독한 채팅 ID 목록 저장"""
        with open('subscribed_chats.txt', 'w', encoding='utf-8') as f:
            for chat_id in self.subscribed_chats:
                f.write(f"{chat_id}\n")
    
    async def send_article_async(self, article: dict, chat_id: str):
        """
        기사 하나를 텔레그램 메시지로 전송 (비동기)
        
        Args:
            article: 기사 정보 딕셔너리
            chat_id: 메시지를 보낼 채팅 ID
        """
        title = article.get('title', '').replace('<b>', '').replace('</b>', '')
        originallink = article.get('originallink', '')
        
        # originallink가 없으면 link 사용
        if not originallink:
            originallink = article.get('link', '')
        
        # 마크다운 형식으로 제목과 링크 구성
        message = f"[{title}]({originallink})"
        
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            print(f"기사 전송 완료 ({chat_id}): {title[:50]}...")
        except TelegramError as e:
            print(f"메시지 전송 오류 ({chat_id}): {e}")
        except Exception as e:
            print(f"예상치 못한 오류 ({chat_id}): {e}")
    
    def send_article(self, article: dict):
        """
        기사 하나를 모든 구독자에게 전송
        
        Args:
            article: 기사 정보 딕셔너리
        
        Returns:
            실패한 채팅 ID 리스트
        """
        if not self.subscribed_chats:
            return []
        
        title = article.get('title', '').replace('<b>', '').replace('</b>', '')
        originallink = article.get('originallink', '')
        
        # originallink가 없으면 link 사용
        if not originallink:
            originallink = article.get('link', '')
        
        # 마크다운 형식으로 제목과 링크 구성
        message = f"[{title}]({originallink})"
        
        # 모든 구독자에게 전송
        failed_chats = []
        for chat_id_str in list(self.subscribed_chats):  # 리스트로 복사하여 반복 중 수정 가능하게
            try:
                # 채팅 ID를 정수로 변환 (텔레그램 API는 정수를 요구)
                try:
                    chat_id = int(chat_id_str)
                except (ValueError, TypeError):
                    chat_id = chat_id_str
                    print(f"⚠️  채팅 ID 변환 경고: {chat_id_str}를 정수로 변환할 수 없습니다.")
                
                # 먼저 채팅 정보 확인 (디버깅용)
                chat_info = None
                try:
                    chat_info = self.loop.run_until_complete(self.bot.get_chat(chat_id=chat_id))
                    chat_type = chat_info.type
                    chat_title = getattr(chat_info, 'title', '알 수 없음')
                    
                    # 봇이 멤버인지 확인
                    try:
                        bot_info = self.loop.run_until_complete(self.bot.get_me())
                        bot_id = bot_info.id
                        bot_member = self.loop.run_until_complete(self.bot.get_chat_member(chat_id=chat_id, user_id=bot_id))
                        member_status = bot_member.status
                        print(f"📋 채팅 정보: {chat_title}")
                        print(f"   타입: {chat_type}, ID: {chat_id} (원본: {chat_id_str})")
                        print(f"   봇 상태: {member_status}")
                        
                        # 관리자 권한 확인
                        if hasattr(bot_member, 'can_post_messages'):
                            can_post = bot_member.can_post_messages
                            print(f"   메시지 전송 권한: {can_post}")
                        
                        # 일반 그룹인 경우 경고
                        if chat_type == 'group':
                            print(f"   ⚠️  일반 그룹(Group)입니다! 봇은 일반 그룹에 메시지를 보낼 수 없습니다.")
                            print(f"   → 그룹을 슈퍼그룹(Supergroup)으로 업그레이드해야 합니다.")
                    except Exception as member_error:
                        print(f"📋 채팅 정보: {chat_title} (타입: {chat_type}, ID: {chat_id})")
                        print(f"   ⚠️  봇 멤버 정보 확인 실패: {member_error}")
                        print(f"   → 봇이 그룹/채널에 추가되지 않았을 수 있습니다.")
                except Exception as info_error:
                    print(f"⚠️  채팅 정보 확인 실패 ({chat_id}): {info_error}")
                    print(f"   → 채팅 ID가 잘못되었거나 봇이 해당 채팅에 접근할 수 없습니다.")
                
                # 비동기 방식으로 전송
                print(f"📤 메시지 전송 시도 중... (채팅 ID: {chat_id})")
                self.loop.run_until_complete(self.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                ))
                print(f"✅ 기사 전송 완료 ({chat_id}): {title[:50]}...")
                time.sleep(0.1)  # 레이트 리밋 방지
            except TelegramError as e:
                error_msg = str(e)
                error_code = getattr(e, 'error_code', None)
                error_description = getattr(e, 'description', None)
                
                # 전체 오류 정보 출력
                print(f"\n{'='*60}")
                print(f"❌ 텔레그램 API 오류 발생")
                print(f"   채팅 ID: {chat_id} (원본: {chat_id_str})")
                print(f"   오류 메시지: {error_msg}")
                print(f"   오류 코드: {error_code}")
                print(f"   오류 설명: {error_description}")
                print(f"{'='*60}\n")
                
                # 채팅 ID로 개인/그룹 구분
                chat_id_str_for_check = str(chat_id)
                is_group = chat_id_str_for_check.startswith('-')
                
                if "Unauthorized" in error_msg or "chat not found" in error_msg.lower():
                    if is_group:
                        # 그룹/채널인 경우
                        print(f"\n❌ 메시지 전송 실패 ({chat_id}): {error_msg}")
                        print(f"   오류 코드: {error_code}")
                        
                        # 채팅 정보가 있으면 타입별로 구체적인 안내
                        if chat_info:
                            chat_type = chat_info.type
                            if chat_type == 'group':
                                print(f"\n   🔍 원인: 일반 그룹(Group)입니다!")
                                print(f"   일반 그룹은 봇이 메시지를 보낼 수 없습니다.")
                                print(f"   'has access to messages'는 메시지를 읽을 수 있다는 의미이며,")
                                print(f"   메시지를 보내려면 슈퍼그룹(Supergroup)이 필요합니다.")
                                print(f"\n   ✅ 해결 방법:")
                                print(f"   1. 그룹 설정 열기")
                                print(f"   2. '그룹을 슈퍼그룹으로 업그레이드' 선택")
                                print(f"   3. 또는 그룹을 채널로 변환")
                            elif chat_type == 'supergroup':
                                print(f"\n   🔍 원인: 슈퍼그룹이지만 권한이 없습니다!")
                                print(f"   봇이 그룹에 추가되어 있지만 메시지를 보낼 권한이 없습니다.")
                                print(f"\n   ✅ 해결 방법:")
                                print(f"   1. 그룹 설정 → 관리자 → 봇을 관리자로 추가")
                                print(f"   2. 또는 봇을 일반 멤버로 추가 (슈퍼그룹은 일반 멤버도 메시지 전송 가능)")
                            elif chat_type == 'channel':
                                print(f"\n   🔍 원인: 채널이지만 권한이 없습니다!")
                                print(f"   채널의 경우 봇을 관리자로 추가하고 '메시지 전송' 권한을 별도로 부여해야 합니다.")
                                print(f"\n   ✅ 해결 방법:")
                                print(f"   1. 채널 설정 → 관리자 → 관리자 추가")
                                print(f"   2. @mapotoday_bot 검색 후 추가")
                                print(f"   3. '메시지 전송' 권한 활성화 (필수!)")
                        else:
                            print(f"\n   가능한 원인:")
                            print(f"   1. 봇(@mapotoday_bot)이 그룹/채널에 추가되지 않았습니다")
                            print(f"   2. 봇이 그룹에서 제거되었습니다")
                            print(f"   3. 일반 그룹(Group)인 경우 → 슈퍼그룹(Supergroup)으로 업그레이드 필요")
                            print(f"   4. 채널의 경우 봇을 관리자로 추가하고 '메시지 전송' 권한 부여 필요")
                            print(f"\n   해결 방법:")
                            print(f"   - 그룹: 그룹 설정 → 멤버 추가 → @mapotoday_bot 검색 후 추가")
                            print(f"   - 채널: 채널 설정 → 관리자 → 관리자 추가 → @mapotoday_bot → '메시지 전송' 권한 활성화")
                    else:
                        # 개인 채팅인 경우
                        print(f"⚠️  메시지 전송 실패 ({chat_id}): {error_msg}")
                        print(f"   → 봇(@mapotoday_bot)에게 먼저 메시지를 보내주세요!")
                    failed_chats.append(chat_id_str)
                elif "bot was blocked" in error_msg.lower() or "bot blocked" in error_msg.lower():
                    print(f"⚠️  메시지 전송 실패 ({chat_id}): 봇이 차단되었습니다")
                    print(f"   → 봇 차단을 해제해주세요")
                    failed_chats.append(chat_id_str)
                else:
                    print(f"⚠️  메시지 전송 오류 ({chat_id}): {e}")
                    print(f"   오류 코드: {error_code}")
                    if is_group:
                        print(f"   → 그룹/채널에 봇이 추가되어 있고 관리자 권한이 있는지 확인해주세요")
            except Exception as e:
                print(f"❌ 예상치 못한 오류 ({chat_id}): {e}")
                import traceback
                traceback.print_exc()
        
        # 권한이 없는 채팅은 구독자 목록에서 제거 (모든 기사 전송 후)
        # 이 함수는 기사별로 호출되므로, 여기서는 제거하지 않고 마지막에 한 번만 제거
        return failed_chats
    
    def check_and_send_news(self):
        """뉴스를 확인하고 새로운 기사를 전송"""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 뉴스 확인 중...")
        
        try:
            # 새로운 기사만 필터링 (내부에서 API 호출)
            new_articles = self.naver_api.get_new_articles(SEARCH_QUERY, display=DISPLAY_COUNT)
            
            if not new_articles:
                print("새로운 기사가 없습니다. (이미 처리된 기사이거나 검색 결과가 없습니다)")
                return
            
            if not self.subscribed_chats:
                print("⚠️  구독자가 없습니다. 기사를 전송할 수 없습니다.")
                print("   → .env 파일에 CHAT_ID를 설정하거나 봇에게 메시지를 보내주세요.")
                return
            
            print(f"✅ {len(new_articles)}개의 새로운 기사를 발견했습니다.")
            
            # 모든 기사 전송 중 실패한 채팅 ID 수집
            all_failed_chats = set()
            
            # 각 기사를 개별 메시지로 전송
            for article in new_articles:
                failed_chats = self.send_article(article)
                if failed_chats:
                    all_failed_chats.update(failed_chats)
                time.sleep(0.5)  # API 레이트 리밋 방지를 위한 짧은 대기
            
            # 모든 기사 전송 후 권한이 없는 채팅 제거
            if all_failed_chats:
                for chat_id in all_failed_chats:
                    self.subscribed_chats.discard(chat_id)
                self._save_subscribed_chats()
                print(f"\n⚠️  권한이 없는 채팅 ID를 구독자 목록에서 제거했습니다: {list(all_failed_chats)}")
                print("   → 봇을 그룹/채널에 추가하거나 봇에게 메시지를 보낸 후 다시 시도해주세요.\n")
        
        except Exception as e:
            print(f"❌ 뉴스 확인 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """봇 실행"""
        print("마포 오늘 뉴스 봇을 시작합니다...")
        print(f"검색어: {SEARCH_QUERY}")
        print(f"체크 간격: 5분")
        print(f"구독자 수: {len(self.subscribed_chats)}")
        
        if not self.subscribed_chats:
            print("\n⚠️  경고: 구독자가 없습니다!")
            print("봇에게 /start 명령을 보내거나 .env 파일에 CHAT_ID를 설정해주세요.")
            print("채팅 ID 확인 방법: @userinfobot 봇에게 메시지를 보내면 확인할 수 있습니다.\n")
        else:
            print("\n💡 중요: 개인 채팅의 경우 봇(@mapotoday_bot)에게 먼저 메시지를 보내야 합니다!")
            print("   봇이 메시지를 보낼 수 있도록 봇과 대화를 시작해주세요.\n")
        
        # 시작 시 한 번 실행
        self.check_and_send_news()
        
        # 5분마다 실행
        schedule.every(5).minutes.do(self.check_and_send_news)
        
        # 스케줄러 실행
        while True:
            schedule.run_pending()
            time.sleep(1)


def main():
    """메인 함수"""
    try:
        bot = MapoTodayBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n봇을 종료합니다.")
    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == '__main__':
    main()
