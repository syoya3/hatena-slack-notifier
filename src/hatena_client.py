import requests
from urllib.parse import quote
from typing import List, Dict, Optional
from datetime import datetime
import time

class HatenaBookmarkClient:
    """はてなブックマークAPIクライアント"""
    
    BASE_URL = "https://b.hatena.ne.jp"
    API_DELAY = 1  # API呼び出し間隔（秒）
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'HatenaSlackNotifier/1.0'
        })
    
    def get_hotentry(self, category: str = "all", limit: int = 30) -> List[Dict]:
        """
        人気エントリを取得
        
        Args:
            category: カテゴリ（it, economics, life, entertainment等）
            limit: 取得件数
        
        Returns:
            記事情報のリスト
        """
        category_key = (category or "").strip().lower()
        urls = []
        if category_key and category_key != "all":
            urls = [
                f"{self.BASE_URL}/hotentry/{category_key}.json",
                f"{self.BASE_URL}/hotentry/{category_key}?mode=json",
                f"{self.BASE_URL}/hotentry/all/{category_key}.json",
            ]

        for url in urls:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 404:
                    continue
                response.raise_for_status()
                try:
                    data = response.json()
                except ValueError:
                    continue
                entries = data.get('entries') if isinstance(data, dict) else data
                if not isinstance(entries, list):
                    continue

                articles = []
                for entry in entries[:limit]:
                    article = self._parse_entry(entry)
                    if article:
                        articles.append(article)
                    time.sleep(self.API_DELAY)  # レート制限対策

                return articles
            except requests.RequestException:
                continue
            except ValueError:
                continue

        return self._get_hotentry_rss(category=category_key, limit=limit)
    
    def get_bookmark_count(self, url: str) -> int:
        """指定URLのブックマーク数を取得"""
        api_url = f"https://bookmark.hatenaapis.com/count/entry?url={url}"
        
        try:
            response = self.session.get(api_url, timeout=5)
            response.raise_for_status()
            return int(response.text)
        except:
            return 0
    
    def get_entry_detail(self, url: str) -> Optional[Dict]:
        """エントリの詳細情報を取得"""
        api_url = f"https://bookmark.hatenaapis.com/entry/json/?url={url}"
        
        try:
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'url': url,
                'title': data.get('title', ''),
                'bookmarks': data.get('count', 0),
                'entry_url': data.get('entry_url', ''),
                'screenshot': data.get('screenshot', ''),
            }
        except:
            return None
    
    def _parse_entry(self, entry: Dict) -> Optional[Dict]:
        """エントリデータをパース"""
        try:
            if 'count' in entry or 'entry_url' in entry:
                title = entry.get('title') or entry.get('subject') or entry.get('comment') or ''
                url = entry.get('url') or entry.get('link') or entry.get('entry_url') or ''
                if not url:
                    return None
                if not title:
                    title = url
                entry_url = entry.get('entry_url', '') or url
                screenshot = entry.get('screenshot', '')
                if not screenshot:
                    screenshot = f"{self.BASE_URL}/entry/image/{quote(url, safe='')}"

                return {
                    'title': title,
                    'url': url,
                    'bookmarks': entry.get('count', 0),
                    'entry_url': entry_url,
                    'date': entry.get('date', ''),
                    'description': entry.get('description', ''),
                    'screenshot': screenshot,
                    'fetched_at': datetime.now().isoformat()
                }

            title = entry.get('title', '')
            url = entry.get('link', '')
            bookmarks = entry.get('hatena_bookmarkcount', entry.get('bookmarkcount', 0))
            try:
                bookmarks = int(bookmarks)
            except (TypeError, ValueError):
                bookmarks = 0
            if not title or not url:
                return None

            entry_url = entry.get('entry_url', '')
            screenshot = ''
            if url:
                detail = self.get_entry_detail(url)
                if detail:
                    entry_url = detail.get('entry_url', entry_url)
                    bookmarks = detail.get('bookmarks', bookmarks)
                    screenshot = detail.get('screenshot', '')
                if not screenshot:
                    screenshot = f"{self.BASE_URL}/entry/image/{quote(url, safe='')}"
            if not entry_url:
                entry_url = url

            return {
                'title': title,
                'url': url,
                'bookmarks': bookmarks,
                'entry_url': entry_url,
                'date': entry.get('published', entry.get('updated', '')),
                'description': entry.get('summary', ''),
                'screenshot': screenshot,
                'fetched_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error parsing entry: {e}")
            return None

    def _get_hotentry_rss(self, category: str, limit: int) -> List[Dict]:
        if not category or category == "all":
            rss_url = f"{self.BASE_URL}/hotentry.rss"
        else:
            rss_url = f"{self.BASE_URL}/hotentry/{category}.rss"
        try:
            response = self.session.get(rss_url, timeout=10)
            response.raise_for_status()

            import xml.etree.ElementTree as ET

            root = ET.fromstring(response.text)
            # Hatena RSS uses RSS 1.0 (RDF) namespaces.
            ns = {
                'rss': 'http://purl.org/rss/1.0/',
                'dc': 'http://purl.org/dc/elements/1.1/',
                'hatena': 'http://www.hatena.ne.jp/info/xmlns#',
            }
            items = root.findall('rss:item', ns)

            articles = []
            for item in items[:limit]:
                entry = {
                    'title': item.findtext('rss:title', default='', namespaces=ns),
                    'link': item.findtext('rss:link', default='', namespaces=ns),
                    'bookmarkcount': item.findtext('hatena:bookmarkcount', default='0', namespaces=ns),
                    'published': item.findtext('dc:date', default='', namespaces=ns),
                    'summary': item.findtext('rss:description', default='', namespaces=ns),
                }
                article = self._parse_entry(entry)
                if article:
                    articles.append(article)
                time.sleep(self.API_DELAY)  # レート制限対策

            return articles
        except Exception as e:
            print(f"Error fetching hotentry: {e}")
            return []
