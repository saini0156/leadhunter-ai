from leadhunter.config import load_env_file, DEFAULT_ENV_PATH
load_env_file(DEFAULT_ENV_PATH)

from leadhunter.db import Database

db = Database()

print("\n" + "=" * 100)
print("RECENT LEADS")
print("=" * 100)

rows = db.conn.execute("""
    SELECT
        id,
        name,
        status,
        qualified,
        lead_tier,
        email_message,
        city
    FROM leads
    ORDER BY id DESC
    LIMIT 20
""").fetchall()

for row in rows:
    print(
        f'{row["id"]} | '
        f'{row["name"]} | '
        f'STATUS={row["status"]} | '
        f'QUALIFIED={row["qualified"]} | '
        f'TIER={row["lead_tier"]} | '
        f'EMAIL={bool(row["email_message"])} | '
        f'CITY={row["city"]}'
    )

print("\n" + "=" * 100)
print("STATUS SUMMARY")
print("=" * 100)

rows = db.conn.execute("""
    SELECT
        status,
        lead_tier,
        qualified,
        COUNT(*) AS n
    FROM leads
    GROUP BY status, lead_tier, qualified
    ORDER BY n DESC
""").fetchall()

for row in rows:
    print(
        f'{row["status"]} | '
        f'TIER={row["lead_tier"]} | '
        f'QUALIFIED={row["qualified"]} | '
        f'COUNT={row["n"]}'
    )

db.close()