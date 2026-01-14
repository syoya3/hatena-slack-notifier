import os
from dotenv import load_dotenv
from .hatena_client import HatenaBookmarkClient
from .article_filter import ArticleFilter
from .slack_notifier import SlackNotifier
from .storage import ArticleStorage

def main():
    """メイン処理"""
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    load_dotenv(dotenv_path)
    print("🚀 はてブ記事収集を開始します...")
    
    # 初期化
    hatena = HatenaBookmarkClient()
    cleanup_days = int(os.environ.get('CLEANUP_DAYS', 90))
    storage = ArticleStorage(cleanup_days=cleanup_days)
    article_filter = ArticleFilter(
        min_bookmarks=int(os.environ.get('MIN_BOOKMARKS', 50)),
        keywords=os.environ.get('KEYWORDS', '').split(',') if os.environ.get('KEYWORDS') else None
    )
    slack = SlackNotifier()
    category = os.environ.get('HATENA_CATEGORY', 'all')
    fetch_limit = int(os.environ.get('FETCH_LIMIT', 50))
    max_notify_count = int(os.environ.get('MAX_NOTIFY_COUNT', 20))
    lookback_days = int(os.environ.get('LOOKBACK_DAYS', 0))
    
    # 既読URL取得
    notified_urls = storage.get_notified_urls(days=lookback_days)
    print(f"📊 既読記事数: {len(notified_urls)}")
    
    # はてブから記事取得
    articles = hatena.get_hotentry(category=category, limit=fetch_limit)
    print(f"📥 取得記事数: {len(articles)}")
    
    # フィルタリング
    filtered_articles = article_filter.filter_articles(articles, notified_urls)
    print(f"✅ 通知対象: {len(filtered_articles)}件")
    
    if not filtered_articles:
        print("通知する記事がありませんでした")
        return
    
    # カテゴリ分類
    category_map = {
        article['url']: article_filter.categorize_article(article)
        for article in filtered_articles
    }
    
    # Slack通知
    slack.send_articles(filtered_articles[:max_notify_count], category_map)
    
    # 既読として記録
    storage.add_notified_articles(filtered_articles)
    
    # 統計表示
    stats = storage.get_statistics()
    print(f"\n📈 統計情報:")
    print(f"  累計通知記事: {stats.get('total_articles', 0)}件")
    print(f"  平均ブックマーク数: {stats.get('avg_bookmarks', 0):.1f}")

if __name__ == "__main__":
    main()
