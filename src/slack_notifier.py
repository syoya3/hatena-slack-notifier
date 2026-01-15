import requests
from typing import List, Dict
import os

class SlackNotifier:
    """Slack通知クライアント"""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.environ.get('SLACK_WEBHOOK_URL')
        
        if not self.webhook_url:
            raise ValueError("Slack Webhook URLが設定されていません")
    
    def send_articles(self, articles: List[Dict], category_map: Dict[str, str] = None):
        """記事をSlackに送信"""
        normalized_articles = self._normalize_articles(articles)
        if not normalized_articles:
            print("通知する記事がありません")
            return
        
        article_blocks = [self._build_article_block(article) for article in normalized_articles]
        # Slack block limit is 50; keep some headroom for header/context/divider.
        max_articles_per_message = 47
        chunks = [
            article_blocks[i:i + max_articles_per_message]
            for i in range(0, len(article_blocks), max_articles_per_message)
        ]

        for index, chunk in enumerate(chunks, start=1):
            blocks = self._build_blocks(
                chunk,
                total_count=len(normalized_articles),
                page=index,
                total_pages=len(chunks),
            )
            payload = {"blocks": blocks}

            try:
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10
                )
                response.raise_for_status()
            except requests.RequestException as e:
                print(f"❌ Slack通知エラー: {e}")
                return

        print(f"✅ {len(normalized_articles)}件の記事をSlackに通知しました")
    
    def _build_blocks(
        self,
        articles: List[Dict],
        total_count: int,
        page: int,
        total_pages: int,
    ) -> List[Dict]:
        """Slack Block Kitメッセージを構築"""
        page_suffix = f" ({page}/{total_pages})" if total_pages > 1 else ""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📚 はてブ注目記事 ({total_count}件){page_suffix}",
                    "emoji": True
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "更新: 最新の人気記事"
                    }
                ]
            },
            {"type": "divider"}
        ]

        for article in articles:
            blocks.append(self._build_article_block(article))

        return blocks
    
    def _build_article_block(self, article: Dict) -> Dict:
        """個別記事のブロックを構築"""
        title = article.get('title') or 'Untitled'
        url = article.get('url') or ''
        bookmarks = article.get('bookmarks', 0)
        entry_url = article.get('entry_url', '') or url
        
        text = f"*<{url}|{title}>*\n"
        text += f"🔖 <{entry_url}|{bookmarks} users>"
        
        block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        }
        
        # サムネイルがあれば追加
        if article.get('screenshot'):
            block["accessory"] = {
                "type": "image",
                "image_url": article['screenshot'],
                "alt_text": title
            }
        
        return block

    def _normalize_articles(self, articles: List[Dict]) -> List[Dict]:
        """記事データをSlack表示用に正規化"""
        normalized = []
        for article in articles:
            url = (article.get('url') or '').strip()
            if not url:
                continue
            title = (article.get('title') or '').strip() or url
            entry_url = (article.get('entry_url') or '').strip() or url
            try:
                bookmarks = int(article.get('bookmarks', 0))
            except (TypeError, ValueError):
                bookmarks = 0

            normalized.append({
                **article,
                'url': url,
                'title': title,
                'entry_url': entry_url,
                'bookmarks': bookmarks,
            })

        return normalized
    
    def _get_category_emoji(self, category: str) -> str:
        """カテゴリの絵文字を取得"""
        emoji_map = {
            'AI/ML': '🤖',
            'Frontend': '🎨',
            'Backend': '⚙️',
            'Mobile': '📱',
            'DevOps': '🚀',
            'Blockchain': '⛓️',
            'Python': '🐍',
            'その他': '📄'
        }
        return emoji_map.get(category, '📄')
