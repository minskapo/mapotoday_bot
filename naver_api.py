import requests
import hashlib
import json
import os
from typing import List, Dict


class NaverNewsAPI:
    """네이버 뉴스 검색 API 클라이언트"""
    
    BASE_URL = "https://openapi.naver.com/v1/search/news"
    
    def __init__(self, client_id: str, client_secret: str, processed_articles_file: str = "processed_articles.json"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.processed_articles_file = processed_articles_file
        self.processed_articles = self._load_processed_articles()
    
    def _load_processed_articles(self) -> set:
        """처리된 기사 ID 목록 로드"""
        if os.path.exists(self.processed_articles_file):
            try:
                with open(self.processed_articles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('article_ids', []))
            except:
                return set()
        return set()
    
    def _save_processed_articles(self):
        """처리된 기사 ID 목록 저장"""
        with open(self.processed_articles_file, 'w', encoding='utf-8') as f:
            json.dump({'article_ids': list(self.processed_articles)}, f, ensure_ascii=False, indent=2)
    
    def _get_article_id(self, article: Dict) -> str:
        """기사 고유 ID 생성 (originallink 기반)"""
        originallink = article.get('originallink', '')
        if not originallink:
            # originallink가 없으면 link 사용
            originallink = article.get('link', '')
        return hashlib.md5(originallink.encode('utf-8')).hexdigest()
    
    def search_news(self, query: str, display: int = 10, sort: str = 'date') -> List[Dict]:
        """
        뉴스 검색
        
        Args:
            query: 검색어
            display: 결과 개수 (10~100)
            sort: 정렬 옵션 ('sim' 또는 'date')
        
        Returns:
            검색 결과 리스트
        """
        headers = {
            'X-Naver-Client-Id': self.client_id,
            'X-Naver-Client-Secret': self.client_secret
        }
        
        params = {
            'query': query,
            'display': min(max(display, 10), 100),  # 10~100 범위로 제한
            'sort': sort,
            'start': 1
        }
        
        try:
            response = requests.get(self.BASE_URL, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('items', [])
        except Exception as e:
            print(f"API 호출 오류: {e}")
            return []
    
    def get_new_articles(self, query: str, display: int = 10) -> List[Dict]:
        """
        새로운 기사만 반환 (중복 제거)
        
        Args:
            query: 검색어
            display: 검색할 결과 개수
        
        Returns:
            새로운 기사 리스트
        """
        articles = self.search_news(query, display=display, sort='date')
        new_articles = []
        
        for article in articles:
            article_id = self._get_article_id(article)
            if article_id not in self.processed_articles:
                new_articles.append(article)
                self.processed_articles.add(article_id)
        
        if new_articles:
            self._save_processed_articles()
        
        return new_articles
