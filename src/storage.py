import json
from pathlib import Path
from typing import Set, Dict, List
from datetime import datetime, timedelta

class ArticleStorage:
    """既読記事の管理"""
    
    def __init__(self, storage_path: str = "data/notified_articles.json", cleanup_days: int = 90):
        self.storage_path = Path(storage_path)
        self.cleanup_days = cleanup_days
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """ストレージファイルの存在確認"""
        if not self.storage_path.exists():
            self._save_data({'articles': []})
    
    def _load_data(self) -> Dict:
        """データ読み込み"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'articles': []}
    
    def _save_data(self, data: Dict):
        """データ保存"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_notified_urls(self, days: int = 30) -> Set[str]:
        """既読URLセットを取得（指定日数以内）"""
        data = self._load_data()
        cutoff_date = None if days <= 0 else datetime.now() - timedelta(days=days)
        
        urls = set()
        for article in data.get('articles', []):
            notified_at = datetime.fromisoformat(article['notified_at'])
            if cutoff_date is None or notified_at > cutoff_date:
                urls.add(article['url'])
        
        return urls
    
    def add_notified_articles(self, articles: List[Dict]):
        """通知済み記事を追加"""
        data = self._load_data()
        
        for article in articles:
            data['articles'].append({
                'url': article['url'],
                'title': article['title'],
                'bookmarks': article['bookmarks'],
                'notified_at': datetime.now().isoformat()
            })
        
        # 古いデータをクリーンアップ（指定日数以上前）
        if self.cleanup_days > 0:
            cutoff = datetime.now() - timedelta(days=self.cleanup_days)
            data['articles'] = [
                a for a in data['articles']
                if datetime.fromisoformat(a['notified_at']) > cutoff
            ]
        
        self._save_data(data)
    
    def get_statistics(self) -> Dict:
        """統計情報を取得"""
        data = self._load_data()
        articles = data.get('articles', [])
        
        if not articles:
            return {}
        
        total_bookmarks = sum(a['bookmarks'] for a in articles)
        
        return {
            'total_articles': len(articles),
            'avg_bookmarks': total_bookmarks / len(articles),
            'max_bookmarks': max(a['bookmarks'] for a in articles),
            'latest_notification': articles[-1]['notified_at'] if articles else None
        }
