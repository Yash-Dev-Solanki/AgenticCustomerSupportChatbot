from agents.summary_agent import fetch_all_chats_by_customer_id
from datetime import datetime, timezone, timedelta

res = fetch_all_chats_by_customer_id("538794")
for chat in res:
    created_at = datetime.fromisoformat(chat['createdAt'].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours= 12)

    if created_at < cutoff:
        break

    print(chat)