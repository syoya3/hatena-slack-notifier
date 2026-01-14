from typing import List, Dict

class ArticleFilter:
    """記事フィルタリング"""
    
    def __init__(self, min_bookmarks: int = 50, keywords: List[str] = None):
        self.min_bookmarks = min_bookmarks
        self.keywords = keywords
        
        # 除外キーワード（ノイズ除去）
        self.exclude_keywords = [
            '炎上', '悲報', 'まとめ', 'なんj'
        ]
    
    def filter_articles(self, articles: List[Dict], notified_urls: set) -> List[Dict]:
        """記事をフィルタリング"""
        filtered = []
        
        for article in articles:
            if self._should_notify(article, notified_urls):
                filtered.append(article)
        
        # ブックマーク数でソート
        filtered.sort(key=lambda x: x['bookmarks'], reverse=True)
        return filtered
    
    def _should_notify(self, article: Dict, notified_urls: set) -> bool:
        """通知すべきか判定"""
        url = (article.get('url') or '').strip()
        title_raw = (article.get('title') or '').strip()
        title = title_raw.lower()
        bookmarks = article.get('bookmarks', 0)

        # 必須項目チェック
        if not url or not title_raw:
            return False

        # 既読チェック
        if url in notified_urls:
            return False
        
        # ブックマーク数チェック
        if bookmarks < self.min_bookmarks:
            return False
        
        # 除外キーワードチェック
        if any(keyword in title for keyword in self.exclude_keywords):
            return False
        
        # キーワードマッチ（より柔軟に）
        if self.keywords:
            # タイトルまたはURLにキーワードが含まれるか
            text = f"{title} {url}".lower()
            if not any(keyword.lower() in text for keyword in self.keywords):
                return False
        
        return True
    
    def categorize_article(self, article: Dict) -> str:
        """記事をカテゴリ分類"""
        title = article.get('title', '').lower()
        url = article.get('url', '').lower()
        text = f"{title} {url}"
        
        categories = {
            'AI/ML': ['ai', 'machine learning', 'deep learning', 'llm', 'gpt', 'neural'],
            'Frontend': ['react', 'vue', 'next.js', 'frontend', 'css', 'javascript'],
            'Backend': ['api', 'database', 'server', 'backend', 'node.js'],
            'Mobile': ['flutter', 'react native', 'ios', 'android', 'mobile'],
            'DevOps': ['docker', 'kubernetes', 'aws', 'gcp', 'ci/cd', 'devops'],
            'Blockchain': ['blockchain', 'web3', 'crypto', 'ethereum', 'bitcoin'],
            'Python': ['python', 'django', 'fastapi', 'pandas'],
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'その他'
