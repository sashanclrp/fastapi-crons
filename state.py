import aiosqlite
from datetime import datetime

class SQLiteStateBackend:
    def __init__(self, db_path: str = "cron_state.db"):
        self.db_path = db_path

    async def set_last_run(self, job_name: str, timestamp: datetime):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS job_state (
                    name TEXT PRIMARY KEY,
                    last_run TEXT
                )
            """)
            await db.execute(
                "INSERT OR REPLACE INTO job_state (name, last_run) VALUES (?, ?)",
                (job_name, timestamp.isoformat())
            )
            await db.commit()

    async def get_last_run(self, job_name: str):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT last_run FROM job_state WHERE name=?", (job_name,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None