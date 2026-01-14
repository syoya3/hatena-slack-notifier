# Hatena Bookmark to Slack Notifier

Hatena Bookmark hot entries to Slack.

## Quick Start

```bash
pip install -r requirements.txt

cat << 'ENV' > .env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
MIN_BOOKMARKS=100
KEYWORDS=
MAX_NOTIFY_COUNT=20
HATENA_CATEGORY=all
FETCH_LIMIT=50
LOOKBACK_DAYS=0
CLEANUP_DAYS=0
ENV

python -m src.main
```

## GitHub Actions (optional)

1. Set secret `SLACK_WEBHOOK_URL` in repository settings.
2. Optional variables (same names as `.env` above).
3. Edit schedule in `.github/workflows/notify.yml` (cron is UTC).

## Customization (optional)

- Filters, excluded words, and categories: `src/article_filter.py`
- Slack message format: `src/slack_notifier.py`
- `LOOKBACK_DAYS=0` will dedupe against all history.
- `CLEANUP_DAYS=0` keeps notified history forever (no cleanup).

## Troubleshooting

- `Slack Webhook URLが設定されていません`: ensure `.env` is loaded or GitHub Secret is set.
- No articles notified: check `MIN_BOOKMARKS` and `KEYWORDS` thresholds.
