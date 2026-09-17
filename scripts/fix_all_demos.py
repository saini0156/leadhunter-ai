import sys, os, re
sys.path.insert(0, os.path.abspath("."))
from leadhunter.db import Database

def slugify(name, city):
    combined = f"{name}-{city}".lower()
    return re.sub(r'[^a-z0-9]+', '-', combined).strip('-')

db = Database("data/leadhunter.db")
rows = db.conn.execute("SELECT id, name, city FROM leads").fetchall()
count = 0
for r in rows:
    slug = slugify(r["name"], r["city"] or "city")
    demo_url = f"/preview/{slug}"
    db.conn.execute(
        "UPDATE leads SET demo_url = ?, demo_status = 'READY' WHERE id = ?",
        (demo_url, r["id"])
    )
    count += 1

db.conn.commit()
print(f"[SUCCESS] Updated {count} leads in database with valid instant demo URLs!")
