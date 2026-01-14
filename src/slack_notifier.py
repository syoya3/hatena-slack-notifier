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
        if not articles:
            print("通知する記事がありません")
            return
        
        blocks = self._build_blocks(articles, category_map)
        payload = {"blocks": blocks}
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            print(f"✅ {len(articles)}件の記事をSlackに通知しました")
        
        except requests.RequestException as e:
            print(f"❌ Slack通知エラー: {e}")
    
    def _build_blocks(self, articles: List[Dict], category_map: Dict[str, str] = None) -> List[Dict]:
        """Slack Block Kitメッセージを構築"""
        category_map = category_map or {}
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📚 はてブ注目記事 ({len(articles)}件)",
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
        
        # カテゴリ別にグループ化
        categorized = {}
        for article in articles:
            category = category_map.get(article['url'], 'その他')
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(article)
        
        # カテゴリごとに表示
        for category, cat_articles in categorized.items():
            emoji = self._get_category_emoji(category)
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{emoji} {category}*"
                }
            })
            
            for article in cat_articles[:5]:  # カテゴリごとに最大5件
                blocks.append(self._build_article_block(article))
        
        return blocks
    
    def _build_article_block(self, article: Dict) -> Dict:
        """個別記事のブロックを構築"""
        title = article['title']
        url = article['url']
        bookmarks = article['bookmarks']
        entry_url = article.get('entry_url', '')
        
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
