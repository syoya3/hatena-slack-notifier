import os

# はてなブックマーク設定
HATENA_CATEGORY = os.environ.get('HATENA_CATEGORY', 'it')
FETCH_LIMIT = int(os.environ.get('FETCH_LIMIT', 50))

# フィルタ設定
MIN_BOOKMARKS = int(os.environ.get('MIN_BOOKMARKS', 50))
KEYWORDS = os.environ.get('KEYWORDS', '').split(',') if os.environ.get('KEYWORDS') else [
    'python', 'react', 'flutter', 'ai', 'blockchain',
    'typescript', 'docker', 'kubernetes', 'aws'
]

# 通知設定
MAX_NOTIFY_COUNT = int(os.environ.get('MAX_NOTIFY_COUNT', 20))
LOOKBACK_DAYS = int(os.environ.get('LOOKBACK_DAYS', 30))

# Slack設定
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
