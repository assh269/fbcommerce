import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.config import settings

print(f"Seeding database: {settings.database_url}")

from seed import seed

asyncio.run(seed())
print("Done! 100 products seeded.")
